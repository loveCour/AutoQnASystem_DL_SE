#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <signal.h>
#include <sys/stat.h>
#include <winsock2.h>

#ifndef WIN32
#include <unistd.h>
#else
#include <winsock.h>
#endif
#include <fcntl.h>

#include "idxbig.h"

#define MAX_WORD_LEN 256
#define ID_COUNT 6

#ifdef WIN32
#pragma comment(lib, "idxdatagen.lib")
#pragma comment(lib, "Reg_System-win32.lib")
#pragma comment(lib, "Ret_System-win32.lib")
#endif

/***********�߰�**************/
typedef struct _SearchList SearchList;//Student ���� �̸� ����
typedef struct _socketStruct socketStruct;//Student ���� �̸� ����
struct _SearchList // SearchList ����ü ����
{
	int docNum;
	int TF;
};
struct _socketStruct {  //nrdata�� ���� �����ǰ���, data�� ������ȣ���� ����Ǿ��ִ�.

	int nrData;

	int data[100];

};
socketStruct dataProcessing();
void Sort(SearchList *base, int n);//����
void sendTomodule(socketStruct txdata);
void ErrorHandling(char* message);

int cnt = 5;       //�����׸�⿡ ���� ����

				   /*******************************************/
int main(int argc, char *argv[])
{
	ibsbSearch *sr = NULL;

	char sname[128] = "bbc";

	initIndex();

	int df = 0;
	int status = selectIndexbyName(sname);
	if (status != 0)
	{
		printf("select Error\n");
		exit(0);
	}
	char sStr[200] = "����&�ҽ���&����";
	int iRetVal = searchString(sStr, &df, &sr, 0);

	RetServer_Lib_Destroy();
	sendTomodule(dataProcessing());
	return EXIT_SUCCESS;
}


socketStruct dataProcessing() {

	socketStruct txData;
	SearchList *base = 0;
	int n = 10, i = 0;
	char *ptr;
	char buffer[50];

	FILE *fp = fopen("./../iif_manager_main_test/Result.txt", "r");    //Result ���� ����Է�

	base = (SearchList *)calloc(n, sizeof(SearchList));
	while (!feof(fp)) {
		fgets(buffer, sizeof(buffer), fp);
		if (buffer[0] == '!') {         //docNum�� TF�� �����Ͽ� Searchlist������
			ptr = strtok(buffer, "!");
			ptr = strtok(NULL, "!");
			base[i].docNum = atoi(ptr);
			ptr = strtok(NULL, "!");
			base[i].TF = atoi(ptr);
			i++;
		}


	}
	fclose(fp);

	Sort(base, n);             //Searchlist sorting

	for (i = 0; i < n; i++)
	{
		printf("docNum : %d TF : %3d\n", base[i].docNum, base[i].TF);
	}


	txData.nrData = cnt;
	for (i = 0; i < cnt; i++)
	{
		txData.data[i] = base[i].docNum;
		printf("%d, ", txData.data[i]);
	}
	free(base);
	//int rem = remove("./../iif_manager_main_test/Result.txt");
	return txData;
}

void Sort(SearchList *base, int n)
{
	SearchList temp;
	int i = 0, j = 0;
	for (i = n; i > 1; i--)
	{
		for (j = 1; j < i; j++)
		{

			if (base[j - 1].TF<base[j].TF)//���� �л��� ������ ���� ��
			{
				//�� ���� ������ ��ȯ
				temp = base[j - 1];
				base[j - 1] = base[j];
				base[j] = temp;
			}
		}
	}
}

void sendTomodule(socketStruct txData)
{
	int portNum = 1234;
	socketStruct TermData;  //client�� �������Ḧ �˷��ִ� ����
	TermData.nrData = 0;   //client���� nrdata�� ������ 0�� ������ ����� �����

	WSADATA wsaData;
	SOCKET hServSock, hClntSock;
	SOCKADDR_IN servAddr, clntAddr;

	int szClntAddr;
	char message[] = "Hello World!";  //error�޼����� ���� ���ڿ�

	if (WSAStartup(MAKEWORD(2, 2), &wsaData) != 0)
		ErrorHandling("WSAStartup() error!");

	hServSock = socket(PF_INET, SOCK_STREAM, 0);

	if (hServSock == INVALID_SOCKET)
		ErrorHandling("socket() error");

	memset(&servAddr, 0, sizeof(servAddr));
	servAddr.sin_family = AF_INET;
	servAddr.sin_addr.s_addr = htonl(INADDR_ANY);
	servAddr.sin_port = htons(portNum);

	if (bind(hServSock, (SOCKADDR*)&servAddr, sizeof(servAddr)) == SOCKET_ERROR)
		ErrorHandling("bind() error");

	if (listen(hServSock, 5) == SOCKET_ERROR)
		ErrorHandling("listen() error");


	szClntAddr = sizeof(clntAddr);

	printf("[Server] Holding at accept \n");
	hClntSock = accept(hServSock, (SOCKADDR*)&clntAddr, &szClntAddr);

	if (hClntSock == INVALID_SOCKET)
		ErrorHandling("accept() error");

	// ������ �κ��̴�. 

	int maxCnt = 5;
	while (1)
	{
		send(hClntSock, (char*)&txData, sizeof(txData), 0);
		Sleep(100);
		break;
	}

	send(hClntSock, (char*)&TermData, sizeof(TermData), 0);
	// ���� ���� 

	printf("Closing Socket \n");
	closesocket(hClntSock);
	closesocket(hServSock);
	WSACleanup();

}



void ErrorHandling(char* message)
{
	fputs(message, stderr);
	fputc('\n', stderr);
	exit(1);
}
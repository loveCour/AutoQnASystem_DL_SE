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

/***********추가**************/
typedef struct _SearchList SearchList;//Student 형식 이름 정의
typedef struct _socketStruct socketStruct;//Student 형식 이름 정의
struct _SearchList // SearchList 구조체 정의
{
	int docNum;
	int TF;
};
struct _socketStruct {  //nrdata는 보낼 문서의개수, data는 문서번호들이 저장되어있다.

	int nrData;

	int data[100];

};
socketStruct dataProcessing();
void Sort(SearchList *base, int n);//정렬
void sendTomodule(socketStruct txdata);
void ErrorHandling(char* message);

int cnt = 5;       //딥러닝모듈에 보낼 개수

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
	char sStr[200] = "독일&소시지&맥주";
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

	FILE *fp = fopen("./../iif_manager_main_test/Result.txt", "r");    //Result 파일 경로입력

	base = (SearchList *)calloc(n, sizeof(SearchList));
	while (!feof(fp)) {
		fgets(buffer, sizeof(buffer), fp);
		if (buffer[0] == '!') {         //docNum과 TF값 추출하여 Searchlist에저장
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

			if (base[j - 1].TF<base[j].TF)//뒤쪽 학생이 점수가 높을 때
			{
				//두 명의 데이터 교환
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
	socketStruct TermData;  //client에 소켓종료를 알려주는 변수
	TermData.nrData = 0;   //client에서 nrdata의 값으로 0을 받으면 통신이 종료됨

	WSADATA wsaData;
	SOCKET hServSock, hClntSock;
	SOCKADDR_IN servAddr, clntAddr;

	int szClntAddr;
	char message[] = "Hello World!";  //error메세지를 위한 문자열

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

	// 보내는 부분이다. 

	int maxCnt = 5;
	while (1)
	{
		send(hClntSock, (char*)&txData, sizeof(txData), 0);
		Sleep(100);
		break;
	}

	send(hClntSock, (char*)&TermData, sizeof(TermData), 0);
	// 소켓 종료 

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
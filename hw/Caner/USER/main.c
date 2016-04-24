/*
   Citrocan
   Copyright (c) 2016 sisoftrg
   The MIT License (MIT)
*/

#include "stm32f10x.h"
#include <stdio.h>

#define USARTx USART2

#define C_BUF_SIZE 16
CanRxMsg RxMessage[C_BUF_SIZE];
int c_buf_r, c_buf_w;
uint8_t c_free;

#define R_BUF_SIZE 128
#define S_BUF_SIZE 4096
int r_buf_w, s_buf_w, s_buf_r;
uint8_t have_cmd, r_buf[R_BUF_SIZE], s_buf[S_BUF_SIZE];

int ignition = 0;

#ifdef USE_FULL_ASSERT
void assert_failed(uint8_t *file, uint32_t line)
{
	while(1);
}
#endif

void delay(int x)
{
	for(; x != 0; x--);
}

void Init_CANRxMes(CanRxMsg *RxMessage)
{
	uint8_t i = 0;

	RxMessage->StdId = 0x00;
	RxMessage->IDE = CAN_ID_STD;
	RxMessage->DLC = 0;
	RxMessage->FMI = 0;
	for(i = 0; i < 8; i++) {
		RxMessage->Data[i] = 0x00;
	}
}

void USB_HP_CAN1_TX_IRQHandler(void)
{
	if(CAN_GetITStatus(CAN1, CAN_IT_TME)) {
		CAN_ClearITPendingBit(CAN1, CAN_IT_TME);
		c_free = 1;
	}
}

void USB_LP_CAN1_RX0_IRQHandler(void)
{
	if(CAN_GetITStatus(CAN1, CAN_IT_FMP0)) {
		CanRxMsg *msg = &RxMessage[c_buf_w];
		c_buf_w = (c_buf_w + 1) % C_BUF_SIZE;
		Init_CANRxMes(msg);
		CAN_Receive(CAN1, CAN_FIFO0, msg);
	}
}

void CAN_TxMsg(int id, int len, uint8_t * data)
{
	while(!c_free);
	c_free = 0;

	CanTxMsg TxMessage;
	TxMessage.StdId = id;
	TxMessage.RTR = CAN_RTR_DATA;
	TxMessage.IDE = CAN_ID_STD;
	TxMessage.DLC = len;
	for(int i = 0; i < len; i++)
		TxMessage.Data[i] = data[i];
	CAN_Transmit(CAN1, &TxMessage);

	printf("S %03x %d", id, len);
	for(int i = 0; i < len; i++)
		printf(" %02x", data[i]);
	printf("\r\n");
}

void CFG_CAN(void)
{
	RCC_ClocksTypeDef RCC_Clocks;
	RCC_GetClocksFreq(&RCC_Clocks);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_AFIO, ENABLE);
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_CAN1, ENABLE);
	SysTick_CLKSourceConfig(SysTick_CLKSource_HCLK);

	NVIC_InitTypeDef NVIC_InitStructure;
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_0);
	NVIC_InitStructure.NVIC_IRQChannel = USB_LP_CAN1_RX0_IRQn;
	NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 0x0;
	NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0x1;
	NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
	NVIC_Init(&NVIC_InitStructure);

	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_0);
	NVIC_InitStructure.NVIC_IRQChannel = USB_HP_CAN1_TX_IRQn;
	NVIC_InitStructure.NVIC_IRQChannelPreemptionPriority = 0x0;
	NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0x0;
	NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
	NVIC_Init(&NVIC_InitStructure);

	GPIO_InitTypeDef GPIO_InitStructure;
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_11;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IPU;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_12;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	CAN_DeInit(CAN1);

	CAN_InitTypeDef CAN_InitStructure;
	CAN_StructInit(&CAN_InitStructure);
	CAN_InitStructure.CAN_TTCM = DISABLE;
	CAN_InitStructure.CAN_ABOM = DISABLE;
	CAN_InitStructure.CAN_AWUM = DISABLE;
	CAN_InitStructure.CAN_NART = DISABLE;
	CAN_InitStructure.CAN_RFLM = DISABLE;
	CAN_InitStructure.CAN_TXFP = DISABLE;
	CAN_InitStructure.CAN_Mode = CAN_Mode_Normal;

	CAN_InitStructure.CAN_SJW = CAN_SJW_1tq;
	CAN_InitStructure.CAN_BS1 = CAN_BS1_2tq;
	CAN_InitStructure.CAN_BS2 = CAN_BS2_3tq;
	CAN_InitStructure.CAN_Prescaler = 48;
	CAN_Init(CAN1, &CAN_InitStructure);

	CAN_FilterInitTypeDef CAN_FilterInitStructure;
	CAN_FilterInitStructure.CAN_FilterNumber = 0;
	CAN_FilterInitStructure.CAN_FilterMode = CAN_FilterMode_IdMask;
	CAN_FilterInitStructure.CAN_FilterScale = CAN_FilterScale_32bit;
	CAN_FilterInitStructure.CAN_FilterIdHigh = 0x0000;
	CAN_FilterInitStructure.CAN_FilterIdLow = 0x0000;
	CAN_FilterInitStructure.CAN_FilterMaskIdHigh = 0x0000;
	CAN_FilterInitStructure.CAN_FilterMaskIdLow = 0x0000;
	CAN_FilterInitStructure.CAN_FilterFIFOAssignment = CAN_FIFO0;
	CAN_FilterInitStructure.CAN_FilterActivation = ENABLE;
	CAN_FilterInit(&CAN_FilterInitStructure);

	c_free = 1;
	c_buf_r = c_buf_w = 0;

	CAN_ITConfig(CAN1, CAN_IT_FMP0, ENABLE);
	CAN_ITConfig(CAN1, CAN_IT_TME, ENABLE);
	CAN_ITConfig(CAN1, CAN_IT_FF0, ENABLE);
	CAN_ITConfig(CAN1, CAN_IT_FOV0, ENABLE);
}

int fputc(int ch, FILE *f)
{
	while((s_buf_w + 1) % S_BUF_SIZE == s_buf_r);
	s_buf[s_buf_w] = (uint8_t) ch;
	s_buf_w = (s_buf_w + 1) % S_BUF_SIZE;
	USART_ITConfig(USARTx, USART_IT_TXE, ENABLE);
	return ch;
}

void USART2_IRQHandler(void)
{
	if(USART_GetITStatus(USARTx, USART_IT_RXNE) != RESET) {
		volatile uint8_t b = USART_ReceiveData(USARTx);
		if(b == '\r' && !have_cmd) {
			have_cmd = r_buf_w;
			r_buf[r_buf_w] = 0;
			r_buf_w = 0;
		} else if(b >= 32 && b <= 127 && !have_cmd && r_buf_w < R_BUF_SIZE - 1)
			r_buf[r_buf_w++] = b;
	}

	if(USART_GetITStatus(USARTx, USART_IT_TXE) != RESET) {
		if(s_buf_r != s_buf_w) {
			USART_SendData(USARTx, s_buf[s_buf_r]);
			s_buf_r = (s_buf_r + 1) % S_BUF_SIZE;
		}
		if(s_buf_r == s_buf_w)
			USART_ITConfig(USARTx, USART_IT_TXE, DISABLE);
	}
}

void CFG_USART(void)
{
	RCC_APB1PeriphClockCmd(RCC_APB1Periph_USART2, ENABLE);
	RCC_APB2PeriphClockCmd(RCC_APB2Periph_GPIOA | RCC_APB2Periph_AFIO, ENABLE);

	NVIC_InitTypeDef NVIC_InitStructure;
	NVIC_PriorityGroupConfig(NVIC_PriorityGroup_0);
	NVIC_InitStructure.NVIC_IRQChannel = USART2_IRQn;
	NVIC_InitStructure.NVIC_IRQChannelSubPriority = 0x0;
	NVIC_InitStructure.NVIC_IRQChannelCmd = ENABLE;
	NVIC_Init(&NVIC_InitStructure);

	GPIO_InitTypeDef GPIO_InitStructure;
	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_2;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_AF_PP;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	GPIO_InitStructure.GPIO_Pin = GPIO_Pin_3;
	GPIO_InitStructure.GPIO_Mode = GPIO_Mode_IN_FLOATING;
	GPIO_InitStructure.GPIO_Speed = GPIO_Speed_50MHz;
	GPIO_Init(GPIOA, &GPIO_InitStructure);

	USART_InitTypeDef USART_InitStructure;
	USART_InitStructure.USART_BaudRate = 460800;
	USART_InitStructure.USART_WordLength = USART_WordLength_8b;
	USART_InitStructure.USART_StopBits = USART_StopBits_1;
	USART_InitStructure.USART_Parity = USART_Parity_No;
	USART_InitStructure.USART_HardwareFlowControl = USART_HardwareFlowControl_None;
	USART_InitStructure.USART_Mode = USART_Mode_Rx | USART_Mode_Tx;
	USART_Init(USARTx, &USART_InitStructure);

	r_buf_w = 0;
	s_buf_w = s_buf_r = 0;
	have_cmd = 0;

	USART_ITConfig(USARTx, USART_IT_RXNE, ENABLE);
	USART_ITConfig(USARTx, USART_IT_TXE, DISABLE);
	USART_Cmd(USARTx, ENABLE);
}

void TickHandler(void)
{
	if(ignition == 1)
		ignition = 2;
}

int main(void)
{
	CFG_USART();
	CFG_CAN();
	delay(2000000);

	if(SysTick_Config(SystemCoreClock / 10)) { // every 100ms
		printf("E CLK\r\n");
	}

	printf("\r\nOK\r\n");

	while(1) {
		if(ignition == 2) {
			ignition = 1;
			CAN_TxMsg(0x036, 8, (uint8_t[]){0x0e, 0x00, 0x06, 0x0b, 0x01, 0x00, 0x00, 0xa0});
		}

		if(have_cmd) {
			//printf("got cmd: %s\r\n", r_buf);

			if(r_buf[0] == 'i') {
				ignition = r_buf[1] == '1' ? 1 : 0;
				printf("I\r\n");
				have_cmd = 0;
				continue;
			}

			int id;
			uint8_t len, data[8];
			int ok = sscanf((const char *)r_buf, "%x %hhd %hhx %hhx %hhx %hhx %hhx %hhx %hhx %hhx", &id, &len, &data[0], &data[1], &data[2], &data[3], &data[4], &data[5], &data[6], &data[7]);
			if(ok >= 2 && ok >= len + 2)
				CAN_TxMsg(id, len, data);
			else
				printf("E %s\r\n", r_buf);
			have_cmd = 0;
		}
		while(c_buf_r != c_buf_w) {
			CanRxMsg *msg = &RxMessage[c_buf_r];
			c_buf_r = (c_buf_r + 1) % C_BUF_SIZE;
			printf("R %03x %d", msg->StdId, msg->DLC);
			for(int i = 0; i < msg->DLC; i++)
				printf(" %02x", msg->Data[i]);
			printf("\r\n");
		}
	}
}

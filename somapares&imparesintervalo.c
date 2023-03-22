#include <stdio.h>
#include <stdlib.h>


int main() {
	int n1;
	int n2;
	int i;
	int pares = 0;
	int impares = 0;
	printf("Insira o comeco e o fim de um intervalo de numeros inteiros: ");
	scanf("%d %d", &n1, &n2);
	
	printf("O intervalo escolhido foi: ");
	
	for(i=n1;i<=n2;i++){
		printf("\n%d\n", i);
		if(i % 2 == 0)
		{
			pares = pares + i;
		}
		else
		{
			impares = impares + i;	
		}
	}
	

	printf("\nA soma dos numeros pares no intervalo e igual: %d", pares);
	printf("\nA soma dos numeros impares no intervalo e igual: %d", impares);
	
	return 0;
}

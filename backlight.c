#include <stdio.h>
#include <string.h>
#include <stdlib.h>

const char * CONTROL = "/sys/class/backlight/intel_backlight/brightness";

int read_current(){

	int b;
	FILE *f = fopen(CONTROL, "r");
	int res = fscanf(f, "%d", &b);
	fclose(f);
	return b;
}

void set_brightness(int b){
	FILE *f = fopen(CONTROL, "w");
	int res = fprintf(f, "%d", b);
	fclose(f);
}

void usage(const char *argv[]){
	fprintf(stderr, "Usage: %s -i|-d <step>\n", argv[0]);
	fprintf(stderr, "\t\t-i: increase brightness with <step>\n");
	fprintf(stderr, "\t\t-d: decrease brightness with <step>\n");
}

int main(int argc, const char *argv[])
{
	if (argc != 3){
		usage(argv);
		return(1);
	}
	if(strcmp(argv[1], "-i") == 0 || strcmp(argv[1], "-d") == 0){
		int b = read_current();
		int s = atoi(argv[2]);
		switch (argv[1][1]) {
			case 'i':
				b += s;
				break;
			case 'd':
				b -= s;
				break;
		}
		set_brightness(b);
	}

	return 0;
}

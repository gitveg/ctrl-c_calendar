#include <iostream>
#include <cstring>
#include <unistd.h>
#include <time.h>
#include <dirent.h>
#include <sys/types.h>
#include <cstdlib>
using namespace std;


typedef struct schedule{
	long long id; 
	string name;
	string place;
	time_t start_time;
	time_t terminal_time;
	string remark;
	struct schedule *next;
} Schedule;

/*
���ܣ����ճ������е�ĳһ����洢���ļ��� 
������
	sche����Ҫ�洢���ճ̽ṹ���ַ 
����ֵ��
	�����ɹ���1 
	����ʧ�ܣ�0 
*/

bool save_to_file(Schedule* sche) {
    FILE* file;
    char filename[100];

    time_t t = time(NULL);
    int offset = 0;

    t*= 100;

    sprintf(filename, "./schedule/%lld.sche", t + offset);

    while (access(filename, F_OK) == 0) {
        ++offset;
        sprintf(filename, "./schedule/%lld.sche", t + offset);
    }

    if (offset >= 100) {
        printf("Too much schedule\n");
        return 0;
    }

    if ((file = fopen(filename, "w")) == NULL) {
        printf("Cannot open file\n");
        return 0;
    }

    fprintf(file, "%s\r\n%s\r\n%lld\r\n%lld\r\n%s\r\n",
        sche->name.c_str(),    
        sche->place.c_str(),  
        (long long)sche->start_time,
        (long long)sche->terminal_time,
        sche->remark.c_str()   
    );

    fclose(file);
    return 1;
}


/*
���ܣ���./schedule�ļ����µ��ճ��ļ�ȫ����ȡ�������У�����һ���ճ������������id�����ļ��� 
������
	sche��ָ���ճ���������ʼָ���ָ�� 
����ֵ��
	�����ɹ���1 
	����ʧ�ܣ�0 
*/

bool read_from_file(Schedule** sche) {
    DIR* dir;
    struct dirent* entry;
    FILE* file;
    char filename[256];

    if ((dir = opendir("./schedule")) == NULL) {
        printf("Cannot open ./schedule directory\n");
        return 0;
    }

    *sche = NULL;
    Schedule* last = NULL;

    while ((entry = readdir(dir)) != NULL) {
    	
    	// �ж��ļ���׺���Ƿ�Ϊ.sche 
    	const char *dot = strrchr(entry->d_name, '.');
	    if (!dot || dot == entry->d_name) {
	    	continue;
		}
	    else {
	        if (strcmp(dot, ".sche")!=0) {
	        	continue;
			}
	    }
	    
	    //�ж��ļ����Ƿ���Ϲ淶
		if (dot - entry->d_name != 12) {
			// λ��������12 
			continue;
		}
		
		for (char *index = entry->d_name; index < dot ; ++index) {
			if(*index < '0' || *index > '9') {
				// �������� 
				continue;
			}
		}
    	
        snprintf(filename, sizeof(filename), "./schedule/%s", entry->d_name);

        if ((file = fopen(filename, "r")) == NULL) {
        	printf("Cannot open file: %s\n", filename);
            continue;
        }

        Schedule* newSchedule = new Schedule;
        char name[256], place[256], remark[256], id[15];
        long long start_time, terminal_time;
		
		// ��ȡ�ļ�����ת��Ϊid
		strncpy(id, entry->d_name, 12);
		id[12] = '\0';
		newSchedule->id = strtoll(id, NULL, 10);
		
        if (fscanf(file, "%256s %256s %lld %lld %256s",
            name, place, &start_time, &terminal_time, remark) == 5) {

            newSchedule->name = name;
            newSchedule->place = place;
            newSchedule->start_time = start_time;
            newSchedule->terminal_time = terminal_time;
            newSchedule->remark = remark;
            newSchedule->next = NULL;

            if (*sche == NULL) {
                *sche = newSchedule;
            }
            else {
                last->next = newSchedule;
            }
            last = newSchedule;
        }
        else {
            delete newSchedule;
            printf("Error reading data from file: %s\n", filename);
        }

        fclose(file);
    }

    closedir(dir);
    return (*sche != NULL);
}


/*
���ܣ����ճ������е�ĳһ������޸Ĵ洢���ļ��� 
������
	sche����Ҫ�洢���޸Ĺ����ճ̽ṹ���ַ 
����ֵ��
	�����ɹ���1 
	����ʧ�ܣ�0 
*/

bool change_to_file(Schedule* sche) {
    FILE* file;
    char filename[100];

    sprintf(filename, "./schedule/%lld.sche", sche->id);

    if ((file = fopen(filename, "w")) == NULL) {
        printf("Cannot open file\n");
        return 0;
    }

    fprintf(file, "%s\r\n%s\r\n%lld\r\n%lld\r\n%s\r\n",
        sche->name.c_str(),    
        sche->place.c_str(),  
        (long long)sche->start_time,
        (long long)sche->terminal_time,
        sche->remark.c_str()   
    );

    fclose(file);
    return 1;
}


/*
���ܣ����ճ������е�ĳһ������޸Ĵ洢���ļ��� 
������
	sche����Ҫ�洢���޸Ĺ����ճ̽ṹ���ַ 
����ֵ��
	�����ɹ���1 
	����ʧ�ܣ�0 
*/

bool delete_file(Schedule* sche) {
    char filename[100];
    sprintf(filename, "./schedule/%lld.sche", sche->id);
    return remove(filename);
}



int main() {

    Schedule* newSchedule = new Schedule;
    newSchedule->id = 1;
    newSchedule->name = "����";
    newSchedule->place = "ͼ���";
    newSchedule->start_time = time(NULL); 
    newSchedule->terminal_time = newSchedule->start_time + 3600; 
    newSchedule->remark = "���Ǳ�ע";
    newSchedule->next = NULL;

  
    if (save_to_file(newSchedule)) {
        cout << "Schedule saved successfully." << endl;
    }
    else {
        cout << "Failed to save schedule." << endl;
    }

 
    Schedule* scheduleList = NULL;
    if (read_from_file(&scheduleList)) {
        cout << "Schedules loaded from file:" << endl;
        Schedule* current = scheduleList;
        while (current != NULL) {
            cout << "ID: " << current->id << endl;
            cout << "Name: " << current->name << endl;
            cout << "Place: " << current->place << endl;
            cout << "Start Time: " << ctime(&current->start_time);
            cout << "End Time: " << ctime(&current->terminal_time);
            cout << "Remark: " << current->remark << endl;
            current = current->next;
        }
    }
    else {
        cout << "Failed to load schedules from file." << endl;
    }

    return 0;
}

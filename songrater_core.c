#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <stdbool.h>

#ifdef _WIN32
    #define EXPORT __declspec(dllexport)
#else
    #define EXPORT 
#endif



EXPORT void free_matrix(void* ptr){
    free(ptr);
}

EXPORT bool album_add(char *album){
    FILE *fptr = fopen("albums.txt","r");

    if(fptr == NULL){
        FILE *album_list = fopen("albums.txt","w");
        if(!album_list) return false;
        fprintf(album_list,"%s : 0.0\n", album);
        fclose(album_list);
        return false; 
    }

    fclose(fptr);
    fptr = fopen("albums.txt","a");
    if(!fptr) return false;

    fprintf(fptr,"%s : 0.0\n", album);
    fclose(fptr);
    return true; 
}

EXPORT bool create_album(char *album){
    FILE *fptr = fopen(album,"r");

    if(fptr == NULL){
        FILE *new_album = fopen(album,"w");
        if(!new_album) return false;
        fclose(new_album);

        album_add(album);
        return true;
    }
    
    fclose(fptr);
    return false;
}

EXPORT bool change_album_rating(char *album, double rating){
    FILE *fptr = fopen("albums.txt","r");
    if(fptr == NULL){
        return false;
    }

    char buffer[200];
    FILE *temp = fopen("temp.txt","w");
    if(!temp) {
        fclose(fptr);
        return false;
    }

    while(fgets(buffer, sizeof(buffer), fptr) != NULL){
        char cur_album[100] = {0};
        int len = strlen(buffer);

        for(int i = 0; i < len; i++){
            cur_album[i] = buffer[i];
            if(buffer[i] == ' ' && buffer[i+1] == ':'){
                cur_album[i] = '\0';
                break;
            }
        }
        
        if(strcasecmp(album, cur_album) != 0){
            fprintf(temp, "%s", buffer);
        } else {
            fprintf(temp, "%s : %.1lf\n", album, rating);
        }
    }
    
    fclose(fptr);
    fclose(temp);
    remove("albums.txt");
    rename("temp.txt", "albums.txt");
    return true;
}

EXPORT bool remove_album(char *album){
FILE *fptr = fopen("albums.txt","r");
    if(fptr == NULL){
        return false;
    }
    
    char buffer[200];
    FILE *temp = fopen("temp.txt","w");
    if(!temp) {
        fclose(fptr);
        return false;
    }
    
    while(fgets(buffer, sizeof(buffer), fptr) != NULL){
        int len = strlen(buffer);
        char cur_album[100] = {0};

        for(int i = 0; i < len; i++){
            
            if(buffer[i] == ' ' && buffer[i+1] == ':'){
                cur_album[i] = '\0';
                break;
            }
            cur_album[i] = buffer[i];
        }
        
        if(strcasecmp(cur_album, album) != 0){
            fprintf(temp, "%s", buffer);
        }
    }
    
    fclose(temp);
    fclose(fptr);
    remove("albums.txt");
    remove(album);
    rename("temp.txt", "albums.txt");
    return true;

}

EXPORT bool add_song(char *song, char *album, double rating){
    FILE *fptr = fopen(album,"a");
    if (fptr == NULL){
        return false;
    }

    fprintf(fptr,"%s : %.1lf\n", song, rating);
    fclose(fptr);
    return true;
}

EXPORT bool remove_song(char *song, char *album){
    FILE *fptr = fopen(album,"r");
    if(fptr == NULL){
        return false;
    }
    
    char buffer[200];
    FILE *temp = fopen("temp.txt","w");
    if(!temp) {
        fclose(fptr);
        return false;
    }
    
    while(fgets(buffer, sizeof(buffer), fptr) != NULL){
        int len = strlen(buffer);
        char cur_song[100] = {0};

        for(int i = 0; i < len; i++){
            cur_song[i] = buffer[i];
            if(buffer[i] == ' ' && buffer[i+1] == ':'){
                cur_song[i] = '\0';
                break;
            }
        }
        
        if(strcasecmp(cur_song, song) != 0){
            fprintf(temp, "%s", buffer);
        }
    }
    
    fclose(temp);
    fclose(fptr);
    remove(album);
    rename("temp.txt", album);
    return true;
}

EXPORT bool change_song_rating(char *song, char *album, double rating){
    FILE *fptr = fopen(album,"r");
    if(fptr == NULL){
        return false;
    }
    
    char buffer[200];
    FILE *temp = fopen("temp.txt","w");
    if(!temp) {
        fclose(fptr);
        return false;
    }

    while(fgets(buffer, sizeof(buffer), fptr) != NULL){
        int len = strlen(buffer);
        char cur_song[100] = {0};

        for(int i = 0; i < len; i++){
            if(buffer[i] == ' ' && buffer[i+1] == ':'){
                cur_song[i] = '\0';
                break;
            }
            cur_song[i] = buffer[i];
        }
        
        if(strcasecmp(cur_song, song) != 0){
            fprintf(temp, "%s", buffer);
        } else {
            fprintf(temp, "%s : %.1lf\n", cur_song, rating);
        }
    }
    
    fclose(temp);
    fclose(fptr);
    remove(album);
    rename("temp.txt", album);
    return true;
}

EXPORT char (*get_all(char *item, char *subitem))[100]{
    char (*return_s)[100] = (char(*)[100])calloc(100, sizeof(*return_s));

    FILE *fptr = fopen(item,"r");
    if(fptr == NULL){
        return return_s;
    }
    
    char buffer[100];
    int x = 0;
    
    while(fgets(buffer, sizeof(buffer), fptr) != NULL && x < 100){
        int len = strlen(buffer);
        char cur[100] = {0}; 
        
        for(int i = 0; i < len; i++){
            if(buffer[i] == '\n' || buffer[i] == '\r'){
                cur[i] = '\0';
                break;
            }
            cur[i] = buffer[i];
        }
        
        strncpy(return_s[x], cur, 99);
        x++;
    }

    fclose(fptr);
    return return_s;
}

int main(){
    return 0;
}

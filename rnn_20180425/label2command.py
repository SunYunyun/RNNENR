#
label2c = {'B-play_time': 'playTime','I-prize_name': 'prizeName','B-director_name': 'directorName','I-actor_name': 'actorName',
            'I-movie_area': 'movieArea','I-movie_language': 'movieLanguage','B-actor_name': 'actorName','B-release_time': 'releaseTime',
            'I-movie_style': 'movieStyle','B-movie_style': 'movieStyle','B-prize_name': 'prizeName','B-movie_area': 'movieArea',
            'I-season': 'Season','I-play_time': 'playTime','O': None,'I-director_name': 'directorName','I-movie_play_duration': 'moviePlayDuration',
            'I-movie_name': 'movieName','B-season': 'Season','B-movie_play_duration': 'moviePlayDuration','I-release_time': 'releaseTime',
            'B-movie_name': 'movieName','B-movie_language': 'movieLanguage'}


def lbel2command(words,predictions_test):
    predictions_test = check_continue(predictions_test)
    # print ' '.join(predictions_test)
    # predictions_test = check_B(predictions_test)
    playTime = ''; prizeName = ''; directorName = '';actorName = ''
    movieArea = ''; movieLanguage = '';releaseTime = ''; movieStyle = ''; Season = ''
    moviePlayDuration = '';movieName='';movieEpsode='';relationship=''

    if predictions_test :
        flag = 0
        for i in predictions_test:
            if i == 'O':
                flag = flag + 1
                continue
            if i == 'B-play_time':
                if playTime:
                    playTime = playTime + ','+words[flag]
                else:playTime = playTime +words[flag]
            elif i == 'I-play_time':
                playTime = playTime + words[flag]
            elif i == 'B-prize_name':
                if prizeName:
                    prizeName = prizeName + ','+words[flag]
                else: prizeName = prizeName + words[flag]
            elif i == 'I-prize_name':
                prizeName = prizeName + words[flag]
            elif i == 'B-director_name':
                if directorName:
                    directorName = directorName +','+words[flag]
                else:directorName = directorName + words[flag]
            elif i == 'I-director_name':
                directorName = directorName + words[flag]
            elif i == 'B-actor_name':
                if actorName:
                    actorName = actorName +','+words[flag]
                else:actorName = actorName + words[flag]
            elif i == 'I-actor_name':
                actorName = actorName + words[flag]
            elif i == 'B-movie_area':
                if movieArea:
                    movieArea = movieArea +','+words[flag]
                else: movieArea = movieArea+words[flag]
            elif i == 'I-movie_area':
                movieArea = movieArea + words[flag]
            elif i == 'B-movie_language':
                if movieLanguage:
                    movieLanguage = movieLanguage + ',' + words[flag]
                else:movieLanguage = movieLanguage + words[flag]
            elif i == 'I-movie_language':
                movieLanguage = movieLanguage + words[flag]
            elif i == 'B-release_time':
                if releaseTime:
                    releaseTime = releaseTime +','+words[flag]
                else:releaseTime = releaseTime + words[flag]
            elif i == 'I-release_time':
                releaseTime = releaseTime + words[flag]
            elif i == 'B-movie_style':
                if movieStyle :
                    movieStyle = movieStyle +','+words[flag]
                else:movieStyle = movieStyle + words[flag]
            elif i == 'I-movie_style':
                movieStyle = movieStyle + words[flag]
            elif i == 'B-season' or i == 'I-season':
                Season = Season + words[flag]
            elif i == 'B-movie_play_duration':
                if moviePlayDuration:
                    moviePlayDuration = moviePlayDuration + ',' + words[flag]
                else: moviePlayDuration = moviePlayDuration + words[flag]
            elif i == 'I-movie_play_duration':
                moviePlayDuration = moviePlayDuration + words[flag]
            elif i == 'B-movie_name':
                if movieName:
                    movieName = movieName + ','+ words[flag]
                else:movieName = movieName + words[flag]
            elif i == 'I-movie_name':
                movieName = movieName + words[flag]
            elif i == 'B-episode' or i == 'I-episode':
                movieEpsode = movieEpsode + words[flag]
            elif i == 'B-relationship':
                if relationship:
                    relationship = relationship+','+words[flag]
                else:relationship = relationship+words[flag]
            elif i == 'I-relationship':
                relationship = relationship + words[flag]

            flag = flag + 1

    command_dict={'playTime':playTime,'award':prizeName,'directorName':directorName,'actor':actorName,'area':movieArea,
                  'language':movieLanguage,'year':releaseTime,'type':movieStyle,'season':Season,'moviePlayDuration':moviePlayDuration,
                  'videoName':movieName,'episode':movieEpsode,'relative':relationship}
    # return playTime,prizeName,directorName ,actorName ,movieArea, movieLanguage , releaseTime , movieStyle , Season , moviePlayDuration
    return command_dict

def check_serial(predictions_test):

    begin=['B-movie_style','B-movie_name','B-season','B-movie_play_duration','B-release_time','B-movie_language','B-movie_area',
           'B-actor_name','B-play_time']
    _len = len(predictions_test)

    for i  in range(_len):
        if predictions_test[i] == 'O':
            continue

        if predictions_test[i] in begin:
           j=i+1
           _label = predictions_test[i].split('-')[1]
           _label = "I-"+_label

           while(predictions_test[j] not in begin and j<_len-1):
               if predictions_test[j] == 'O':
                   predictions_test[j] = _label
               j=j+1
    return predictions_test

def check_moivename(predictions_test):

    _len = len(predictions_test)
    for i  in range(_len):
        if predictions_test[i] == 'O':
            continue
        elif predictions_test[i] == 'B-movie_name':
            s=[val for val in range(i,_len,1) if predictions_test[val]=='I-movie_name']
            if s== []:
                break
            for j in range(i+1,s[-1]+1,1):
                if predictions_test[j]=='I-movie_name':
                    continue
                else:predictions_test[j]='I-movie_name'
            break
    return predictions_test

def check_continue(predictions_test):
    '''
    B-movie_name I-actor_name I-actor_name O O O
    :return: B-actor_name I-actor_name I-actor_name O O O
    '''
    _len = len(predictions_test)
    i=0
    while(i<_len):
        lables={}
        flag=1
        if predictions_test[i]=='O':
            i = i +1
            continue
        elif predictions_test[i].split('-')[0]=='B':
            j = i+1
            lables[predictions_test[i].split('-')[1]] = 1
            while(j<_len):
                if predictions_test[j] == 'O':
                    break
                l = predictions_test[j].split('-')#'B-movie_name'
                if l[0]=='B' and l[1]!=predictions_test[i].split('-')[1]:
                    break
                elif l[0]=='I' and l[1]==predictions_test[i].split('-')[1]:
                    lables[l[1]] = lables[l[1]]+1
                    j = j+1
                    flag = flag+1
                    continue
                elif l[0]=='I' and l[1]!=predictions_test[i].split('-')[1]:
                    flag = flag + 1
                    if l[1] not in lables:
                        lables[l[1]] = 1
                    else:lables[l[1]] = lables[l[1]]+1
                j = j+1

        if lables.__len__()!=1 and lables.__len__()!=0:
            l = filter(lambda  x:max(lables.values())==lables[x],lables)[0]
            # gflag=0
            # for key,value in lables.items():
            #     if key.split('-')[0] == l:
            #         gflag = gflag + 1.txt
            #         continue
            #     else:
            #         predictions_test[i + gflag] = 'I-'+l
            #         if gflag == 0:
            #             predictions_test[i + gflag] = 'B-'+l
            #         gflag = gflag+1.txt
            val = sum(lables.values())
            for ij in range(i,i+val,1):
                if predictions_test[ij].split('-')[1] != l:
                    predictions_test[ij] = 'I-' + l
                    if ij == i:
                        predictions_test[ij] = 'B-' + l
        i = i + flag

    return predictions_test

def check_B(predictions_test):

    k=0
    while(k<len(predictions_test)):
        i = predictions_test[k]
        if i == 'O':
            k = k+1
            continue
        l = i.split('-')
        if l[0] == 'I':
            j = k-1
            while(j>-1):
                if predictions_test[j].split('-')[0] == 'I':
                    j = j -1
                elif predictions_test[j] == 'O':
                    break
                elif predictions_test[j].split('-')[0] == 'B':
                    j = k
                    break
            if j != k:
                predictions_test[j] = 'B-'+l[1]

        k = k + 1
    return predictions_test


if __name__ == '__main__':

    # check_moivename([u'O', u'O', u'O', u'B-director_name', u'I-director_name', u'O', u'O', u'O', u'B-movie_name', u'I-movie_name' ,u'I-movie_name', u'I-movie_name'])
    # check_continue([u'O', u'O', u'O', u'B-director_name', u'I-director_name', u'O', u'O', u'O', u'B-movie_name', u'I-director_name' ,u'I-movie_name', u'I-movie_name'])
    print check_continue([u'O', u'O' ,u'O', u'B-movie_area', u'I-prize_name'])
    # check_B([u'O', u'O',u'O',u'I-movie_name',u'B-season'])

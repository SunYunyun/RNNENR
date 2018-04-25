#encoding:utf-8

from config_database import clients
import re

class Multi_character_star(object):

    def __init__(self, origal,command,manyFlag,searcherEngine,TermQuery,Term,relation,relation_alis):

        self.flag = 0
        self.origal = origal
        self.command = command
        self.relationship=relation
        self.relation_alias = relation_alis
        self.final = {}
        self.label = ''
        self.actors=set()#[]
        self.profession=[]
        self.relation_ship={}


        if manyFlag:
            self.single_actor(searcherEngine, TermQuery, Term)
            if not self.final:
                fi_actor = self.split_character(self.command,searcherEngine, TermQuery, Term)
                if fi_actor:
                    self.actors.add(fi_actor)
                self.rest_actors(fi_actor, searcherEngine, TermQuery, Term)
            else:
                for _,v in self.final.items():
                    self.actors.add(v)
        else:
            self.single_actor(searcherEngine,TermQuery,Term)

    def split_character(self,actor_list,searchertv,TermQuery,Term):

        def search(tmp, searchertv, TermQuery, Term):
            # query = TermQuery(Term("formatNames", tmp))
            # scoreDocs = searchertv.search(query, 10).scoreDocs

            scoreDocs = clients.query_formates(tmp, 10)

            ts_ = ''
            ta_ = ''
            tmp_= ''
            fflag=0
            figure=''
            mflag = 0
            rflag=0
            # print "%s total matching documents." % len(scoreDocs)
            if len(scoreDocs) != 0:
                for doc in scoreDocs:
                    # doc = searchertv.doc(scoreDoc.doc)
                    ts_ = doc.get("label")
                    ta_ = doc.get('formatName')
                    # break
                if ts_ == 'film':
                    mflag=1
                    m = tmp.encode('utf-8')
                if ts_ == 'figure':
                    fflag=2
                    figure= tmp.encode('utf-8')
                elif ts_ == 'role':
                    rflag=3
                    tmp_=tmp.encode('utf-8')

                if mflag==1 :
                    return m
                elif mflag==0 and fflag==2:
                    return figure
                elif mflag == 0 and fflag ==0 and rflag ==3:
                    return tmp_
                else:return ''
            else:return ''

        clen = len(actor_list)
        i=1
        fi = 0
        flag = 0
        ts=''
        while(fi<clen):

            tmp = actor_list[0:3+(i-1)*3]
            ts = search(tmp, searchertv, TermQuery, Term)
            j = 1
            if ts!='':
                tsf = ts
                fj = fi
                while(fj<=clen and tsf):
                    tmp = actor_list[0:3+(i-1+j)*3]
                    tsf = search(tmp, searchertv, TermQuery, Term)
                    if tsf:
                        ts = tsf
                        j = j+1
                        fj = 3+(i-1+j)*3
                    else:
                        flag=1
                        break
            if flag :
                break
            i = i + j
            fi = i*3
        return ts

    def rest_actors(self, fi_actor,searchertv,TermQuery,Term):

        rest = self.command[self.command.index(fi_actor) + len(fi_actor):]
        if rest not in self.relationship:
            s=rest
            numflag=0
            while (rest and s):
                s = self.split_character(rest,searchertv,TermQuery,Term)
                rest = self.command[self.command.index(s)+len(s):]
                if s:
                    self.actors.add(s)
                numflag = numflag + 1
                if numflag > 7:
                    break
        else:
            if rest in self.relation_alias:
                self.relation_ship['relative']=self.relation_alias[rest]
            else:self.relation_ship['relative'] = rest

    def single_actor(self,searchertv,TermQuery,Term):

        # query = TermQuery(Term("formatNames", self.command))
        # scoreDocs = searchertv.search(query, 3).scoreDocs

        scoreDocs = clients.query_formates(self.command,3)

        tp = {}
        tflag=0;roleflag=0;
        # print "%s total matching documents." % len(scoreDocs)
        if len(scoreDocs) != 0:
            dflag=0;aflag=0;bflag=0
            for doc in scoreDocs:
                # doc = searchertv.doc(scoreDoc.doc)
                ts_ = doc.get("label")
                if ts_=='role':
                    roleflag=1
                ta_ = doc.get('formatName')
                tp_=''
                if 'profession'in doc:tp_ = doc['profession']
                if ts_ in ['appname', 'station']:
                    continue
                elif ts_== 'figure':
                    tflag=1
                    for i in tp_:
                        if i in ['compose','producer','photographer']:
                            continue
                        elif i == 'singer':
                            continue
                        elif ('配 音' in self.origal or u'配 音' in self.origal):
                            tp['dubbing']=ta_.encode('utf-8')
                            bflag=1
                            break
                        elif ('自 导 自 演' in self.origal):
                            tp['director'] = ta_.encode('utf-8')
                            tp['actor'] = ta_.encode('utf-8')

                        elif ('导 演' in self.origal or u'导 演 的' in self.origal or '导'in self.origal):
                            tp['director']=ta_.encode('utf-8')
                            dflag=1
                            break
                        elif ('主 演' in self.origal or '演 的' in self.origal or '演'in self.origal
                              or '出 演' in self.origal or '参 演' in self.origal or '参 演 的' in self.origal) and '导' not in self.origal :
                            # if 'actor' in tp_ and 'director' not in tp_:
                            tp['actor']=ta_.encode('utf-8')

                            aflag=1
                        # elif not re.findall(r'导',self.origal):#20180115 d
                        #     if 'direcor' in tp:
                        #         tp.pop('director')



                        else:
                            if self.command in tp.values() and i.encode('utf-8') in tp.keys():
                                pass
                            else:
                                tp[i.encode('utf-8')]=ta_.encode('utf-8')
                elif ts_== 'film':
                    if 'name' in tp:
                        tp['name'] = "%s///%s"%(tp['name'],ta_.encode('utf-8'))
                    else:
                        tp['name'] = ta_.encode('utf-8')
                else:tp[ts_.encode('utf-8')]=ta_.encode('utf-8')
                if aflag or bflag or dflag:
                    break
                # break
            if tflag and roleflag:
                del tp['role']
            if aflag:
                #self.final = {'actor': self.command}
                self.final = tp #20180115 s

            elif dflag:
                #self.final = {'director': self.command}
                self.final = tp #20180115 s
            elif 'name' in tp:
                if '///' in tp['name']:
                    self.final = {'name':self.command}
                    # self.label = 'name'
                else:
                    self.final = tp
                    # self.label = 'name'
            else:self.final = tp
        else:
            self.final = {}


if __name__ == '__main__':

    s = '好想看南非的电影啊请快点'

    for i in range(len(s)):
        if s[0:i*3] == s:
            break
        print s[0:i*3]



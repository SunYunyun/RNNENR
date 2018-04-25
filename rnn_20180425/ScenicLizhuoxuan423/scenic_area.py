
# coding: utf-8

# In[ ]:
import codecs
import os
path = os.getcwd()+'/ScenicLizhuoxuan423'
class ScenicAreaEntityExtraction():
    
    f=codecs.open(os.path.join(path,"all scenic names.txt"), "r",'utf-8')
    lines=f.readlines()
    f.close()
    
    names=[]
    for line in lines:
        names.append(line.strip())
        
    @staticmethod
    def scenic_area_entity_extraction(sentence):
        
        scenic_name=""
        place_name=""
        flag=1
        
        while flag==1:
        
            for name in ScenicAreaEntityExtraction.names:
            
                if name in sentence:
                    sentence=sentence.replace(name,"")
                
                    if scenic_name:
                        scenic_name=scenic_name+","+name
                    else:
                        scenic_name=scenic_name+name
                    
                    continue
                
                flag=0
        
        result={"place_name":place_name,"scenic_name":scenic_name}
        
        return result


# In[ ]:

if __name__ == '__main__':

    # string=input()
    string = u'山海关'


    result=ScenicAreaEntityExtraction.scenic_area_entity_extraction(string)
        #python2中传入参数应为unicode类型
    print(result['scenic_name'])



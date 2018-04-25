#encoding:utf-8
from  Classicdxq import trie_bys_getname_20180412
from ScenicLizhuoxuan423 import scenic_area
#from ErrorVideoYingxin import ConfigError,proofCheck
import sys
reload(sys)

sys.setdefaultencoding('utf-8')
print trie_bys_getname_20180412.Classify(u'我想看大角湾海上丝路旅游区')
# print scenic_area.ScenicAreaEntityExtraction.scenic_area_entity_extraction(u'我想看山海关')
# result=scenic_area.ScenicAreaEntityExtraction.scenic_area_entity_extraction(u'我想看山海关')
# print(result['scenic_name'])

# target = proofCheck.ProofCheck()
# txt = '放一下急诊科医生'
# resultVIDEO = target.ErrorSuggestMUVIDEO(u"%s" %txt,ConfigError.clients.redundentVideo(),
#                                          'semantic:error_correct:stopword4Video',
#                                          'semantic:error_correct:ConfusingVideo','FILM'
# )
# print resultVIDEO
string = u'我想看'
result=scenic_area.ScenicAreaEntityExtraction.scenic_area_entity_extraction(string)
        #python2中传入参数应为uscenic_namenicode类型
print result
if result.get('scenic_name'):
    print result['scenic_name']
else:print 0
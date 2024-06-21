class Extractor:
    def __init__(self):
        self.sg_keys = ['sim', 'net', 'grp', 'minutes', 'hms', 'calls', 'reject', 'failed', 'coffs', 'smses']
        self.vbm_keys = ['module', '-', 'reset', 'minutes', 'hms', 'calls', 'reject', 'failed', 'coffs', 'smses']

    def get_index(self, str_txt)->list:
        indexes = []
        for i in range(len(str_txt)):
            if '[Statistics of calls on module #' in str_txt[i] or '------------------------------------------------------------------------------' in str_txt[i]:
                indexes.append(i)
        del indexes[:4]
        return indexes

    def remove_char(text:str)->str:
        return text.replace('\n','').replace('\r','').replace('(','').replace(')','')

    def format_dict(self, text:list, keys:list)->dict:
        result = dict()
        text = text.split(' ')
        if '(' in text:
            text.remove('(')
        text = [i for i in text if i != '']
        for i in range(len(text)):
            result[keys[i]] = self.remove_char(text[i])
        # add ASR column calls/calls+failed
        calls = int(result['calls'])
        failed = int(result['failed'])
        calls_failed = calls + failed
        try:
            asr = (calls/calls_failed) * 100
            result['asr'] = round(asr, 1)
        except ZeroDivisionError:
            result['asr'] = 0
        return result

    def format_list(self, raw_list:list,keys:list,module_no:int)->list:
        result = []
        for item in raw_list:
            data_dict = self.format_dict(item,keys)
            data_dict['module'] = '#m' + str(module_no)
            result.append(data_dict)
        return result

    def sg_extractor(self, txt_file):
        indexes = self.get_index(txt_file)
        result = []
        for i, start in enumerate(range(2,len(indexes),5)):
            data_per_module = txt_file[indexes[start]+1:indexes[start]+5]
            data_per_module = self.format_list(data_per_module, self.sg_keys,i)
            result.extend(data_per_module)
        return result

    def vbm_extractor(self, txt_file):
        indexes = self.get_index(txt_file)
        result = []
        for i, idx in enumerate(range(6,len(indexes),5)):
            data_per_module = [txt_file[indexes[idx]+1]]
            data_per_module = self.format_list(data_per_module, self.vbm_keys,i)
            result.extend(data_per_module)
        return result
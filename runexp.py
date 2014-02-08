#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 27 16:26:33 2013

@author: flam
"""



import ConfigParser,argparse,sys,subprocess,os,string

config_default={'tasklist':"",
                'OAR_mail':"",
                'OAR_p':"",
                'OAR_l':"",
                'OAR_name':"",
                'OAR_output':"",
                'taskname':"{task}",
                "varlist":"",
                'param':'',
                'run_type':'direct'}
#                'format_order':"task,taskname,param,cmd,OAR_mail,OAR_p,OAR_l,OAR_name,OAR_output"

not_listed=['Config','Default'];

default_file=os.path.expanduser('~/.config/run_job.ini')

def load_config(c_file):
    """
    Safe config file loading function
    """
    try:
        config = ConfigParser.ConfigParser()
        config.optionxform = str
        config.readfp(open(c_file))
        config=config._sections
        #print config
    except IOError:
        config=None         
    return config
    
def get_tasklist(config):
    lst=list()
    for key in config:
        if not key in not_listed:
            lst.append(key)
    return lst
    

    
def get_default():
    conf=load_config(default_file)
    if conf:
        for key in conf['Default']:
            config_default[key]=conf['Default'][key]
    

def get_default_dict(config):
    res=config_default.copy()
    if 'Config' in config:
        for key in config['Config']:
            res[key]=config['Config'][key]
    if 'Default' in config:
        for key in config['Default']:
            res[key]=config['Default'][key]
    return res

def get_task_dict(config,task):
    default=get_default_dict(config)
    res=default.copy()
    for key in config[task]:
        res[key]=config[task][key] 
    return res
    
def to_list(strng):
    if strng.find(":")>=0:
        ls=strng.split(":")
        res=[]
        if len(ls)<3:
            res=[str(val) for val in range(int(ls[0]),int(ls[1])+1)]
        if len(ls)==3:
            res=[str(val) for val in range(int(ls[0]),int(ls[2])+1,int(ls[1]) )]
    elif strng.find(";")>=0:
        res=strng.split(";")
    return res 

def get_dic_list(dic,varlist,lstvar):
    res=list()
    if lstvar:
        loop=True
    else:
        loop=False
        res.append(dic)
    it=[0 for var in varlist]
    itmax=[len(lst) for lst in lstvar]
    
    nbvar=len(varlist)
    i2=0
    while loop:
        temp=dic.copy()
        for i in range(nbvar):
            temp[varlist[i]]=lstvar[i][it[i]]
        res.append(temp)
        it[0]+=1    
        for i in range(nbvar-1):
            if it[i]==itmax[i]:
                it[i]=0
                it[i+1]+=1
        if it[nbvar-1]==itmax[nbvar-1]:
            loop=False
        #print it
    return res
        
        
def format_dic(dic):
    dic['task']=dic['__name__']
    dic['format_order']=get_format_order(dic)
    
    if dic['format_order']:
        
        fmt_list=dic['format_order'].split(',')
        # formar variables
        for fmt in fmt_list:
            dic[fmt]= dic[fmt].format(**dic)
        
        # generate cmd for oar
        dic['OAR_cmd']=  get_oar_cmd(dic)  
    else:
        dic['cmd']=''
        dic['OAR_cmd']=''
        print "Error formating command (unknown variable or recursive references)"

    return dic
    
def get_oar_cmd(dic):
    res='oarsub'
    if dic['OAR_l']:
        res+=' -l {0}'.format(dic['OAR_l'])
    if dic['OAR_p']:
        res+=' -p {0}'.format(dic['OAR_p'])
    if dic['OAR_name']:
        res+=' -n {0}'.format(dic['OAR_name'])
    if dic['OAR_output']:
        res+=' -O {0} -E {0}'.format(dic['OAR_output'])  
    if dic['OAR_mail']:
        res+=' --notify mail:{0}'.format(dic['OAR_mail'])  
    res+=' -S "{0}"'.format(dic['cmd'])  
    return res

def run_command(cmd,args):
    proc=subprocess.Popen(cmd,shell=True)
    if args.wait:
        proc.wait()

def force_run_type(dic,args):
    if args.runonly:
        dic['run_type']='direct'
    if args.oar:
        dic['run_type']='oar'        
    return dic

def run_task(config,args):
    task=args.task
    dic=get_task_dict(config,task)
    
    # handle force execute
    dic=force_run_type(dic,args)
    
    # handle all dynamic variables
    if dic['varlist']:
        varlist=dic['varlist'].split(',')
    else:
        varlist=list()
    lstvar=list()
    for var in varlist:
        lstvar.append(to_list(dic[var]))
    
    # generate list of jobs and format them
    lst=get_dic_list(dic,varlist,lstvar)
    lst2=[format_dic(dic2) for dic2 in lst]
    
    # select jobs if idx selection given
    if args.idx:
        lsttemp=list()
        for i in args.idx:
            if i<len(lst2):
                lsttemp.append(lst2[i])
            else:
                print "Warning: idx element out of range (no job launched)"
        lst2=lsttemp
    
    # execute all jobs
    if args.test:
        for tsk in lst2:
            if tsk['run_type']=='direct':
                print tsk['cmd']
            elif tsk['run_type']=='oar':
                print tsk['OAR_cmd']                    
            else:
                print "Error: unknown run_type"
    else:
        for tsk in lst2:
            if tsk['run_type']=='direct':
                run_command(tsk['cmd'],args) 
            elif tsk['run_type']=='oar':
                run_command(tsk['OAR_cmd'],args)                     
            else:
                print "Error: unknown run_type"
                        
            
def print_task_info(task,config):
    tsk=get_task_dict(config,task)
    print "Task Name:",tsk['__name__']
    print "Command:",tsk['cmd']
    print "Param.:",tsk['param']
    print "Var. list:",tsk['varlist']

def print_task_info_verbose(task,config):
    tsk=get_task_dict(config,task)
    print "Task Name:",tsk['__name__']
    for key in tsk:
        print key,':',tsk[key]
    
    tsk['task']=tsk['__name__']
    print "Format order:",get_format_order(tsk)


def get_dependence(txt):
    frmt=string.Formatter();
    temp=frmt.parse(txt)
    #print temp
    res=[v[1] for v in temp if v[1]]
    return res
    
def get_dependences(dic):
    res=dict()
    for key in dic:
        res[key]=get_dependence(dic[key])
    return res

def strs_in_list(strs,lst):
    res=True
    for st in strs:
        if not st in lst:
            res=False
    return res

def get_format_order(dic):
    keys=list(dic.keys())
    #print dic
    depends=get_dependences(dic)
    #print depends
    levels=list()
    
    sub_keys=list()
    
    lev = [key for key in keys if not depends[key]]
    #print lev
    sub_keys.extend(lev)
    rem_key=  [key for key in keys if not key in sub_keys]
    #print rem_key
    #print rem_key
    levels.append(lev)
    nbrem=len(rem_key)
    error=0
    while rem_key:
        lev = [key for key in rem_key if strs_in_list(depends[key],sub_keys)]
        #print lev
        sub_keys.extend(lev)
        rem_key=  [key for key in rem_key if not key in sub_keys]
        levels.append(lev)
        if nbrem==len(rem_key):
            error=1
            break
        nbrem=len(rem_key)
        #print rem_key
    
        #print lev
    #print levels
    
    res=""
    for lv in levels:
        res+=",".join(lv)+','
    if error:
        res=''
    else:
        res=res[:-1]
    #print res
    return res



def main(argv):  

    parser = argparse.ArgumentParser(prog='runexp',
                                     formatter_class=argparse.RawDescriptionHelpFormatter,
        description='''utility for launching parallel jobs (direct execution or oarsub)''',
    epilog='''''')   
    
    parser.add_argument('-c','--configfile', type=str, nargs=1,
                   help='config file (jobs.ini in current folder)',action="store",default='jobs.ini')  
    parser.add_argument('-l','--list',action='store_true',help='show list of tasks') 
    parser.add_argument('-t','--test',action='store_true',help='test task launching (print commands)') 
    parser.add_argument('-r','--runonly',action='store_true',help='force direct run of command (without oarsub)') 
    parser.add_argument('-o','--oar',action='store_true',help='force the use of oarsub') 
    parser.add_argument('-v','--verbose',action='store_true',help='use verbose printing mode')
    parser.add_argument('-i','--info',action='store_true',help='print informtion on the selected task')
    parser.add_argument('-w','--wait',action='store_true',help='wait for the command to terminate (either oarsub or direct run)') 
    parser.add_argument('task',  type=str, nargs='?',help='selected task',default="")
    parser.add_argument('idx',  type=int, nargs='*',help='subtask index(s) for selected execution')
   
    args= parser.parse_args()   
    
    get_default()    
    
    config=load_config(args.configfile)
    
    if config==None:
        print 'no config file'       
    else:
        lst_task=get_tasklist(config)
        #print "config file ok"
        #print get_tasklist(config)
        if args.list or args.task=="":
            print "Task list:\n\t",
            print "\n\t".join(get_tasklist(config))
        elif args.info:
            if args.task in lst_task:
                if args.verbose:
                    print_task_info_verbose(args.task,config)                
                else:   
                    print_task_info(args.task,config)
            else:
                print "Error: Not a valid task"            
        else:
            if args.verbose:
                print "Run task {task}".format(task=args.task)
            if args.task in lst_task:
                run_task(config,args)
            else:
                print "Error: Not a valid task"
            


if __name__ == "__main__":
   #import doctest
   #doctest.testmod(verbose=True)   
   main(sys.argv[1:])
   #print get_dependence('./launch_octave.sh {module} {script} {param}')

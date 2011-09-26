#!/usr/bin/python
# vim:expandtab:autoindent:tabstop=4:shiftwidth=4:filetype=python:tw=0
# Copyright (c) 2011, Dell Inc.
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#    * Redistributions of source code must retain the above copyright
#       notice, this list of conditions and the following disclaimer.
#     * Redistributions in binary form must reproduce the above copyright
#       notice, this list of conditions and the following disclaimer in the
#       documentation and/or other materials provided with the distribution.
#     * Neither the name of the Dell, Inc. nor the
#       names of its contributors may be used to endorse or promote products
#       derived from this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL Dell, Inc. BE LIABLE FOR ANY DIRECT, INDIRECT,
# INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT
# LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
# PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY OF
# LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING NEGLIGENCE
# OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
#
#
# #############################################################################
# Filename: pushattr.py
# Version: 1.0
# Authors: Sharad Naik
import sys
import os, time
from xml.dom.minidom import parse
import xml.dom.minidom
from iniparse import ConfigParser 
from os import system, popen3

# =============================================================================
class CNARunner:
    '''
    Transforms lists of tests into lists of results.
    '''
    def __init__(self, idracIp, idracUser, idracPass, file, attrSet, flag):
        '''
        Takes a list of strings, which (for now) must be both a valid file name, and the name of the testcase-derived class inside that file.
        '''
        self.idracIp = idracIp
        self.idracUser = idracUser
        self.idracPass = idracPass
        self.confFile = file
        self.settings = attrSet
        self.flagSet  = flag
        self.run()
        
    def run(self):
      if (self.settings == 'bios'):
        service = "BIOS"
        job_service = "BIOSService"
      elif (self.settings == 'nic'):
        service = "NIC"
        job_service = "NICService"
      elif (self.settings == 'idrac'):
        service = "iDRACCard"
        job_service = "iDRACCardService"
      config = self.parseConfig(self.confFile)
      tempOrderedList = config
      jobs = []
      if len(config) >= 1:
        if (self.flagSet != "Commit"):
          print "\n"
          print "Now setting attributes..."
          print "\n"
          for nic in tempOrderedList:
            attNames = config[nic][0]
            attValues = config[nic][1]
            f = self.setNICAttributes(nic, attNames, attValues, service, self.settings)
            if (self.settings == "idrac"):
              command = "wsman invoke -a ApplyAttributes http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_" + service + "Service?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_" + service + "Service,SystemName=DCIM:ComputerSystem,Name=DCIM:" + service + "Service -J " + f.name + " -h " + self.idracIp + " -P 443 -u " + self.idracUser + " -p " + self.idracPass + " -V -v -c dummy.cert -j utf-8 -y basic -m 512 -O AttList.xml"
              msg_string = "ApplyAttributes_OUTPUT"
              tmpList2 = self.runCommand(command)
              outlines = open('AttList.xml', 'U').readlines()
              idrac_job = self.parseInstanceID(outlines)
              if idrac_job != None:
                print "Config job id:" + idrac_job + " for:" + nic + " has been created."
                jobs.append(idrac_job)
            else:
              command = "wsman invoke -a SetAttributes http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_" + service + "Service?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_" + service + "Service,SystemName=DCIM:ComputerSystem,Name=DCIM:" + service + "Service -J " + f.name + " -h " + self.idracIp + " -P 443 -u " + self.idracUser + " -p " + self.idracPass + " -V -v -c dummy.cert -j utf-8 -y basic -m 512 -O AttList.xml"
              msg_string = "SetAttributes_OUTPUT"
              tmpList2 = self.runCommand(command)

            self.msgOutput(nic, msg_string)
          print "\n"

        if (self.flagSet != "Set" and self.settings != "idrac"):
          jobs = []
          count = 0
          for keys in tempOrderedList:
            count = count + 1
            if count == len(config):
              print "Setting up config job for " + keys  
              resp = self.createNICConfigJob(job_service, keys, '1')
              jid =self.parseInstanceID(resp[1])
            else:
              resp = self.createNICConfigJob(job_service, keys)
              jid =self.parseInstanceID(resp[1])
            if jid == None:
              print "Failed to get the job id from CreateTargetedConfigJob. \n"
            else:
              print "Config job id:" + jid + " for:" + keys + " has been created."
              jobs.append(jid)
        
          print "\n" + "Restarting target server to execute configuration jobs."
          print "\n"    

          self.processJobids(jobs, 10)
          print 'Restarting server.'

          command = "wsman invoke -a GetRSStatus http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LCService?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_LCService,SystemName=DCIM:ComputerSystem,Name=DCIM:LCService -h " + self.idracIp + " -P 443 -u " + self.idracUser + " -p " + self.idracPass + " -V -v -c dummy.cert -j utf-8 -y basic"
          rsstat = "Ready"
          while (rsstat == "Ready"):
            data = self.runCommand(command)
            rsstat = self.parseRSStatus(data[1])
            sys.stdout.write(".")
            sys.stdout.flush()

          if (rsstat != "Ready" and rsstat != None):
            print "Checking for Remote Services Ready...."

          while (rsstat != "Ready" and rsstat != None):
            data = self.runCommand(command)
            rsstat = self.parseRSStatus(data[1])
            sys.stdout.write(".")
            sys.stdout.flush()

          if (rsstat == "Ready"):
            print "Server is Ready.."

        elif (self.settings == "idrac"):
          if (len(jobs) != 0):
             self.processJobids(jobs, 5)
  
          
    def processJobids(self, jobs, sleep_time):
       total_jobs = 0
       total_jobs = len(jobs)
       jobs_completed = 0
       ofile = open('ConfigJobs.txt', 'wb')
       time.sleep(sleep_time)
       sys.stdout.write("Checking job status:")
       sys.stdout.flush()
       while(True):
         ret_list = self.jobStatus(jobs)
         for r in ret_list:
           js_string = self.valueFor("JobStatus>", r)
           if js_string == None:
             ofile.write('Lost iDRAC connectivity while updating\r\n')
             print '\n Lost iDRAC connectivity while updating\n'
           else:
             js_key = js_string.find("<")
             js = js_string[0:js_key]

             if "Failed" == js:
               jobid = self.valueFor("InstanceID>", r)
               job_id = jobid[0:16]
               jobs.remove(job_id)
               jobs_completed = jobs_completed + 1
               test_failed = 1
             elif "Completed" == js:
               jobid = self.valueFor("InstanceID>", r)
               job_id = jobid[0:16]
               jobs.remove(job_id)
               jobs_completed = jobs_completed + 1
               print "\n" + "Job:" + job_id + " completed."
             elif "Completed with Errors" == js:
               jobid = self.valueFor("InstanceID>", r)
               job_id = jobid[0:16]
               ofile.write("Update task successfully completed with errors for the job id: " + "\r\n")
               jobs.remove(job_id)
               jobs_completed = jobs_completed + 1
               print "\n" + "Update task successfully completed for one or more attributes, but with errors!"
             else:
               sys.stdout.write(".")
               sys.stdout.flush()
               time.sleep(sleep_time)

         if jobs_completed == total_jobs: #changes de3-Final on the number of devices
           print 'All job executions complete.'

           break

       ofile.close()


    # Runs the input wsman  command  
    def runCommand(self, command):
        '''
        Executes command and returns a dictionary.
        '''
        tmpStr = ""
        commandOutList = []
        (fin, fout, ferr) = os.popen3(command, "t")
        fin.close()
        commandOutList.append(command)
        tmpStr = self.smoosh(fout.read())
        commandOutList.append(tmpStr.split('\n'))
        commandOutList.append(ferr.read())
        return commandOutList
        
    def smoosh(self, thing):  # message the output of a command
        '''
        >>> print Shell().smoosh("blah")  #  leave normal strings alone
        blah
        >>> print Shell().smoosh("blah\\n")  # strip trailing blanklines
        blah
        >>> print Shell().smoosh(["blah\\n"])  # if thing is one item list, return the item (smooshed)
        blah
        '''
        if type([]) == type(thing):  # if return is a list of one item, return just the item.
            newthing = []
            for l in thing:
                if '\n' == l[-1:]:
                    newthing.append(l[:-1])
                else:
                    newthing.append(l)
            thing = newthing
                    
            if 1 == len(thing):
                thing = thing[0]
        if type("") == type(thing):  # if return is a string with a newline, strip newline.
            if '\n' == thing[-1:]:
                thing = thing[:-1]
        return thing
      

    # Creates the Bios or NIC set attributes file

    def setNICAttributes(self, nic, attnames, attvalues, service, settings):
        '''
        Sets the current value for the NIC attribute "attname" to "attvalue"
        '''
        if type(attnames) != list:
            attnames = [attnames]
        attnamestring = ''
        if type(attvalues) != list:
            attvalues = [attvalues]
        attvaluestring = ''
        for att in attnames:
            attnamestring = attnamestring + "<p:AttributeName>" + att + "</p:AttributeName>\r\n"
        for attvalue in attvalues:
#            attvalue = self.specialCharacters(attvalue) #This handels special characters
            attvaluestring = attvaluestring + "<p:AttributeValue>" + attvalue + "</p:AttributeValue>\r\n"    
        f = open(nic + "_setatts.xml", "w")
        if (settings == 'idrac'):
          setatt = '''<p:ApplyAttributes_INPUT xmlns:p="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_''' + service + '''Service">''' + "\r\n" + '''<p:Target>''' + nic + '''</p:Target>''' + "\r\n" + attnamestring + attvaluestring + '''</p:ApplyAttributes_INPUT>'''
        else:
          setatt = '''<p:SetAttributes_INPUT xmlns:p="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_''' + service + '''Service">''' + "\r\n" + '''<p:Target>''' + nic + '''</p:Target>''' + "\r\n" + attnamestring + attvaluestring + '''</p:SetAttributes_INPUT>'''

        f.write(setatt)
        f.close()
        return f
        
      
    def specialCharacters(self, XMLstring = 'example greater than > less than < ampersand & single quote "'):#Handles strings with characters that cause problems for XML files.
        '''
        Filter the input to XML files.  Certain characters need to be translated for XML input.
        config.ini Input    Change to
        <                     &lt;  
        >                     &gt;
        "                     &quot;  
        &                     &amp;  
        see link http://en.wikipedia.org/wiki/List_of_XML_and_HTML_character_entity_references
        '''
        #& must be first as all will introduce more &s.  If ; is added this will cause a problem.
        XMLstring = XMLstring.replace('&','&' + 'amp' + ';')
        #do not put anything above this & MUST be first!!!!
        
        XMLstring = XMLstring.replace('<','&' + 'lt' + ';')
        XMLstring = XMLstring.replace('>','&' + 'gt' + ';')
        XMLstring = XMLstring.replace('"','&' + 'quot' + ';')
        XMLstring = XMLstring.replace("'",'&' + 'apos' + ';')
        XMLstring = XMLstring.replace('*','&' + 'times' + ';')
        XMLstring = XMLstring.replace('|','&' + 'brvbar' + ';')
        XMLstring = XMLstring.replace('-','&' + 'macr' + ';')
        XMLstring = XMLstring.replace('~','&' + 'tilde' + ';')
        XMLstring = XMLstring.replace('-','&' + 'ndash' + ';') 
        XMLstring = XMLstring.replace('^','&' + 'circ' + ';')
        return XMLstring
      
    # Creates the targeted config job for BIOS or NIC
    def createNICConfigJob(self, jobService, nic=None, rebootType=None): 
        '''
        Create a job to set configuration attributes for attribute - "nic".
        '''
        return self.createTargetedConfigJobMethod(jobService, nic, rebootType)
      
    def createTargetedConfigJobMethod(self, jobService, jobType=None, rebootType=None):
        rebootjobstring = ''
        if rebootType != None:
            rebootjobstring = '''<p:RebootJobType>'''+ rebootType +'''</p:RebootJobType> \r\n'''
        f = open((jobType + "_createTargetedConfigJob.xml"), "w")
        ConfigJobInput = '''<p:CreateTargetedConfigJob_INPUT xmlns:p="http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_''' + jobService + '''">
  <p:Target>''' + jobType + '''</p:Target> \r\n''' + rebootjobstring + '''<p:ScheduledStartTime>TIME_NOW</p:ScheduledStartTime>
  <p:UntilTime>20111111111111</p:UntilTime>
</p:CreateTargetedConfigJob_INPUT>'''
        f.write(ConfigJobInput)
        f.close()
        command = "wsman invoke -a CreateTargetedConfigJob http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_" + jobService + "?SystemCreationClassName=DCIM_ComputerSystem,CreationClassName=DCIM_" + jobService + ",SystemName=DCIM:ComputerSystem,Name=DCIM:" + jobService + " -J " + f.name + " -h " + self.idracIp + " -P 443 -u " + self.idracUser + " -p " + self.idracPass + " -V -v -c dummy.cert -j utf-8 -y basic"
        r = self.runCommand(command)
        return r
        
    def parseInstanceID(self, data):  # Return string following InstanceID in the given data.
        ''' Pull the instance id from the given data.
        >>> print wsman().parseInstanceID(["blah", "blah", "                Selector: InstanceID = JID_001247818173, __cimnamespace ", "blah"])
        JID_001247818173
        '''
        if type("") == type(data):
            data = data.split("\n")
            
        if type([]) == type(data):
            marker = "InstanceID"
            for l in data:
                ndx = l.find(marker)
                if not -1 == ndx:
                    ndx2 = l[(ndx + 2 + len(marker)):].find("<")
                    if -1 == ndx2:
                        return None
                    else:
                        return l[(ndx + 2 + len(marker)):((ndx + 2 + len(marker)) + ndx2)]
        return None
      
    # Gets the RSSTATUS from the LC after the Job is complete and reboot starts.

    def parseRSStatus(self, data):  # Return string following Status in the given data.
        if type("") == type(data):
           data = data.split("\n")
            
        if type([]) == type(data):
            marker = "<n1:Status>"
            for l in data:
               ndx = l.find(marker)
               if not -1 == ndx:
                    ndx2 = l[(ndx + len(marker)):].find("<")
                    if -1 == ndx2:
                        ndx3 = l[(ndx + len(marker)):].find(" ")
                        if -1 == ndx3:
                            return l[(ndx + len(marker)):((ndx + len(marker)) + len(l))] # assuming InstanceID is the last string in the line.
                        else:
                            return l[(ndx + len(marker)):((ndx + len(marker)) + ndx3)]
                    else:
                        return l[(ndx + len(marker)):((ndx + len(marker)) + ndx2)]
        return None

    def jobStatus(self, jid, device = None):  # device is a dictionary with dev['ElementName'],dev['InstanceID']
        '''
        jid is a job id or list of job ids
        '''
        return_list = list() #return_list is a list containing job ids.
        if type(jid) != list:
            command = "wsman get http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob?InstanceID=" + str(jid) + " -h " + self.idracIp + " -P 443 -u " + self.idracUser + " -p " + self.idracPass + " -V -v -c dummy.cert -j utf-8 -y basic"
            r = self.runCommand(command)
            js = self.valueFor("JobStatus>", r)
            jn = self.valueFor("Name>", r)
            ms = self.valueFor("Message>", r)
            msid = self.valueFor("MessageID>", r)
            
            if None == js:
                print "iDRAC connectivity might be lost while updating. Please wait till it gets back."                        
            else:
                print str(jid) +" has status:- "  + str(js) + ", Message:- " + str(ms) + ", and MessageID:- " + str(msid)
            return r
        else:
            for j in jid:
                #log.info('Current Job Status(' + str(j) + ')')
                command = "wsman get http://schemas.dmtf.org/wbem/wscim/1/cim-schema/2/root/dcim/DCIM_LifecycleJob?InstanceID=" + j + " -h " + self.idracIp + " -P 443 -u " + self.idracUser + " -p " + self.idracPass + " -V -v -c dummy.cert -j utf-8 -y basic"
                r = self.runCommand(command)
                js = self.valueFor("JobStatus>", r)
                jn = self.valueFor("Name>", r)
                if None == js:
                        print "iDRAC connectivity might be lost while updating. Please wait till it gets back."
                        return_list.append(r)
                else:
                    if device != None:
                        for key in device.iterkeys():
                            #print str(key) + ' dev[key] ' + str(device[key])
                            #print jn
                            if str(key) == str(jn):
                                return_list.append(r)
                        if str(jn) =='Reboot1':
                            return_list.append(r)
                    else:
                        return_list.append(r)
                    if jid.index(j) == (len(jid) - 1): #FIXME : checking if all the jobs are done, changes depending on the number of updates to be scheduled
                        break 
            return return_list
          
    def valueFor(self, key, resp):
      ''' Return the value that matches the given key in the command output.
      >>> r = Response(None, ["blah", "Message = success"], None, None)
      >>> print r.valueFor("Message =")
      success
      ''' 
      # FIXME : delete this after taking the calls to it out of wsman
      x = resp[1]
      key = key.lstrip()
      if not None == x:
        if type("") == type(x):
          x = x.split("\n")
        if type([]) == type(x):
          for line in x:
            ndx = line.find(key)
            if not ndx == -1:
#              if ndx == 10:#Check to see if the line begins with "key"
              return line[ndx+len(key):].lstrip()
            else:
              continue
                        
                                                
        return None
      
    # Go through the output of Set Attributs and print the error messages
    def msgOutput(self, fqdd, msg_string):

       DOMTree = xml.dom.minidom.parse("AttList.xml")
       root_elem = DOMTree.documentElement

       attoutput_tag = root_elem.getElementsByTagNameNS('*', msg_string)
       if len(attoutput_tag) == 0:
         print "No Attributes To Set. Exiting the Program"
         sys.exit(-1)

       # Get the Namespace prefix and use that to get output data

       for attr_out in attoutput_tag:
         prefix = attr_out.prefix

         msglist  = root_elem.getElementsByTagName(prefix + ':Message')
         msgargslist  = root_elem.getElementsByTagName(prefix + ':MessageArguments')
         msgidlist    = root_elem.getElementsByTagName(prefix + ':MessageID')

         if len(msgargslist) == 0: 
           print "No Attributes To Set. Exiting the Program"
           sys.exit(-1)

         print fqdd
         i = 0
         marker = " success"
         for msgid in msgidlist:
            l =  msglist[i].childNodes[0].data
            ndx = l.find(marker)
            if -1 == ndx:
               print "   " + msgid.childNodes[0].data + ":" + msglist[i].childNodes[0].data
            i = i + 1
  

    def parseConfig(self, masterConfig):
      '''
      >>> parseConfig('bogus.file')
      {}

      I would expect to see the message in the log... how do I see that here?    
      '''
      config = {}
      tmpList = ["",""]
      cp = ConfigParser()
      cp.optionxform = str
      # LEFP - need log entry here if config file is missing - say using defaults.
      if os.path.isfile(masterConfig) != True:
        print "Your config file: " + masterConfig + " cannot be found!"
        sys.exit(-1)
      cp.read(masterConfig)
      for sec in cp.sections():
        tmpList[0] = cp.options(sec)
        for opt in cp.options(sec):
          if (opt[0:1] != "#"):         # Ignore comments
            tmpStr = cp.get(sec, opt)
            if tmpList[1] != "":
               s = tmpList[1] + "," + tmpStr
               tmpList[1] = s
            else:
               tmpList[1] = tmpStr 
        tmpList[1] = tmpList[1].split(",")
        config[sec] = tmpList
        tmpList = ["",""]
      return config 
  


# =============================================================================
# Main Program, gets the input values and calls the routine in the main class
if __name__ == '__main__':
  bRunCNA = True
  try:
    idracIp = sys.argv[1]
    idracUser = sys.argv[2]
    idracPass = sys.argv[3]
    file = sys.argv[4]
    attrSet = sys.argv[5]
    flag = sys.argv[6]
  except IndexError: #This error happens if you do not specify a file
    print "USAGE: pushattr.py <IPADDRESS> <USERNAME> <USERPASSWORD> <INIFILE> (nic | bios | idrac) Now"
    print "For example: python pushattr.py 192.168.0.111 admin admin123 file.ini nic Now"
    bRunCNA = False
  if bRunCNA == True:
    CNARunner(idracIp, idracUser, idracPass, file, attrSet, flag)

# =============================================================================
# End of code
# =============================================================================


# coding: utf-8

# In[ ]:


import pandas as pd
import matplotlib
#load each csv file as a dataframe
fraud = pd.read_csv('Deepsight URL Reputation Fraud.csv', low_memory=False)
bot = pd.read_csv('Deepsight-IP Reputation Bot.csv', low_memory=False)
spam = pd.read_csv('Deepsight IP Spam.csv', low_memory=False)
c2 = pd.read_csv('Deepsight IP Reputation CNC.csv', low_memory=False)
malware = pd.read_csv('Deepsight IP Reputation Malware.csv', low_memory=False)
phishing = pd.read_csv('Deepsight IP Reputation Phishin.csv', low_memory=False)
attack = pd.read_csv('Deepsight URL Reputation Attack.csv')
url_c2 = pd.read_csv('Deepsight URL Reputation CNC.csv', low_memory=False)
openPhish = pd.read_csv('[KQ] openphish - all.csv', low_memory=False)


# In[1]:


#extract ip and asn from each 
fraud_xml = pd.DataFrame(fraud, columns=['Id', 'xml.domain.ipAddresses.ip.address', 'xml.domain.ipAddresses.ip.asn'])
fraud_domain = pd.DataFrame(fraud, columns=['Id', 'domain.ipAddresses.ipAddress.address', 'domain.ipAddresses.ipAddress.asn'])
bot = bot[["Id","ip.address", "ip.asn"]]
spam = spam[["Id", "ip.address", "ip.asn"]]
c2 = c2[["Id","ip.address","ip.asn"]]
malware = malware[["Id","ip.address","ip.asn"]]
phishing = phishing[["Id","ip.address","ip.asn"]]
attack = attack[['Id', 'xml.domain.ipAddresses.ip.address', 'xml.domain.ipAddresses.ip.asn']]
url_c2 = url_c2[['Id', 'xml.domain.ipAddresses.ip.address', 'xml.domain.ipAddresses.ip.asn']]
openPhish = openPhish[['Id', 'ip_src','asn.src']]


# In[ ]:


#rename columns/format for joining
fraud_xml = fraud_xml.rename(columns={'xml.domain.ipAddresses.ip.address':'ip', 'xml.domain.ipAddresses.ip.asn':'asn'})
fraud_domain = fraud_domain.rename(columns={'domain.ipAddresses.ipAddress.address':'ip','domain.ipAddresses.ipAddress.asn':'asn'})
bot = bot.rename(columns={'ip.address':'ip', 'ip.asn':'asn'})
spam = spam.rename(columns={'ip.address':'ip','ip.asn':'asn'})
c2 = c2.rename(columns={'ip.address':'ip','ip.asn':'asn'})
malware = malware.rename(columns={'ip.address':'ip','ip.asn':'asn'})
phishing = phishing.rename(columns={'ip.address':'ip','ip.asn':'asn'})
attack = attack.rename(columns={'xml.domain.ipAddresses.ip.address':'ip', 'xml.domain.ipAddresses.ip.asn':'asn'})
url_c2 = url_c2.rename(columns={'xml.domain.ipAddresses.ip.address':'ip', 'xml.domain.ipAddresses.ip.asn':'asn'})
openPhish['asn.src'] = openPhish['asn.src'].str.replace('AS', '')
openPhish = openPhish.rename(columns={"ip_src":"ip", "asn.src":"asn"})



# In[1]:



#aggregate our dataframes to one dataframe of columns: identifier, ip, asn
df_aggregate = pd.concat([fraud_xml,fraud_domain,bot,spam,c2,malware,phishing,attack,url_c2,openPhish], sort=True)
df_aggregate = df_aggregate[pd.notnull(df_aggregate["ip"])]


# In[49]:


# graph count of ASN occurance / data analytics stuff here

asn_count = df_aggregate["asn"].value_counts()

#rename axis in order to create a dataframe from the output of value_counts
count = asn_count.rename_axis("asn").reset_index(name="count")

#get the top 10 most occuring asn's - just as a test of our aggregating function
top_10 = count.nlargest(10,'count')


# In[56]:


top_10.plot.barh(x='asn',y='count')


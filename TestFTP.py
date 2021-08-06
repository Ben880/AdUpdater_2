import ftplib

host = "ftp.bbhc.xyz"
username = "ben"
password = ""
# Use secure mode?
secure = True
# Use passive mode?
passive = False

ftps = ftplib.FTP_TLS(host)

with ftps:
    # enable TLS
    ftps.auth()
    ftps.prot_p()
    ftps.login(username, password)
    ftps.cwd('/Civic/Versions')
    with open('powerpoint.ppsx', 'wb') as fp:
        ftps.retrbinary('RETR 2021-07-25-15-28-00.ppsx', fp.write)
    ftps.dir()



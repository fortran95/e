# -*- coding: UTF-8 -*-
def tuple_join(tp):
    r = ''
    for i in tp:
        r += ' ' + str(i)
    return r.strip()
def pgp_translator(pgpinfo):
    retdict = {'text':'','valuable':False,'sign':False,'sender':'','trust':0}
    """
    [GNUPG:] ENC_TO 7F1DBD1EC2218D71 16 0
[GNUPG:] USERID_HINT 7F1DBD1EC2218D71 benchmark
[GNUPG:] NEED_PASSPHRASE 7F1DBD1EC2218D71 1222C7F73FE8B948 16 0
[GNUPG:] GOOD_PASSPHRASE
[GNUPG:] BEGIN_DECRYPTION
[GNUPG:] PLAINTEXT 62 1336666675 tempinfo_newkey
[GNUPG:] PLAINTEXT_LENGTH 84
[GNUPG:] SIG_ID cFi3MrQcfWKcvglX1fAHMD8czOY 2012-05-10 1336666675
[GNUPG:] GOODSIG 6650AD717D831A9C NERV Devkey (用于ATF系统的开发调试) <fortran95@126.com>
[GNUPG:] VALIDSIG 2002F0DE79CFD4FA0F1F3F626650AD717D831A9C 2012-05-10 1336666675 0 4 0 1 8 00 2002F0DE79CFD4FA0F1F3F626650AD717D831A9C
[GNUPG:] TRUST_ULTIMATE
[GNUPG:] DECRYPTION_OKAY
[GNUPG:] GOODMDC
[GNUPG:] END_DECRYPTION"""
    lines = pgpinfo.split('\n')
    ret = ''
    for l in lines:
        a = l.split(' ')
        if len(a) < 2:
            continue
        if a[1] == 'ENC_TO':
            ret += '[GPG] 收件人ID：%s\n' % a[2]
        elif a[1] == 'USERID_HINT':
            ret += '[GPG] 收件人为：\n  %s\n' % tuple_join(a[3:])
        elif a[1] == 'PLAINTEXT':
            ret += '[GPG] 已经解密，明文输出开始\n'
        elif a[1] == 'PLAINTEXT_LENGTH':
            ret += '[GPG] 明文长度确认为 %s 字节\n' % a[2]
        elif a[1] == 'GOODSIG':
            ret += '[GPG] 发现签名，来自：\n  %s\n' % tuple_join(a[3:])
        elif a[1] == 'VALIDSIG':
            ret += '[GPG] 签名确认有效！\n'
            retdict['sign'] = True
            retdict['sender'] = a[2]
        elif a[1] == 'DECRYPTION_OKAY':
            ret += '[GPG] 解密成功\n'
        elif a[1] == 'BEGIN_DECRYPTION':
            retdict['valuable'] = True
        elif a[1] == 'END_DECRYPTION':
            ret += '[GPG] 解密完毕\n'
        elif a[1] in ('NODATA','NO_SECKEY','DECRYPTED_FAILED'):
            ret += '[GPG] 无法完成解密和验证\n'
            retdict['valuable'] = False
            break
        elif a[1][0:6] == 'TRUST_':
            retdict['trust'] = {'UNDEFINED':-1,'NEVER':0,'MARGINAL':1,'FULLY':2,'ULTIMATE':3}[a[1][6:]]
        else:
            print "gpgtranslator: %s" % l
    retdict['text'] = ret
    return retdict
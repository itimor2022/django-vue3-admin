# coding=utf-8
import boto3
import re
import sys


class S3Helper(object):
    """
    需要下载boto3模块
    """

    def __init__(self):
        self.access_key = S3_FILE_CONF.get("ACCESS_KEY")
        self.secret_key = S3_FILE_CONF.get("SECRET_KEY")
        self.region_name = S3_FILE_CONF.get("REGION_NAME")

        # 连接s3
        self.s3 = boto3.resource(
            service_name='s3',
            region_name=self.region_name,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    def upload_file_s3(self, file_name, bucket, s3_dir):
        """
        上传本地文件到s3指定文件夹下
        :param file_name: 本地文件路径
        :param bucket: 桶名称
        :param s3_dir:要上传到的s3文件夹名称
        :return: 上传成功返回True，上传失败返回False，并打印错误
        """
        res = sys.platform
        p = re.compile(r'\w{1}')
        s = p.search(res).group()

        if s == 'w':
            p = re.compile(r'.*\\(.*)(\..*)')
        else:
            p = re.compile(r'.*/(.*)(\..*)')
        file = ""
        if p.search(file_name):
            s1 = p.search(file_name).group(1)
            s2 = p.search(file_name).group(2)
            file = s1 + s2
        s3_file = s3_dir + file
        try:
            self.s3.Object(bucket, s3_file).upload_file(file_name)
        except Exception as e:
            print('出错了：' + str(e))
            return False
        return True


if __name__ == '__main__':
    S3_FILE_CONF = {
        "ACCESS_KEY": "aaa",
        "SECRET_KEY": "bbb",
        "REGION_NAME": "ap-east-1",
    }
    UPLOAD_FILE_NAME = sys.argv[1]
    UPLOAD_BUCKET_NAME = sys.argv[2]
    UPLOAD_S3_DIR = sys.argv[3]
    s3 = S3Helper()
    res = s3.upload_file_s3(UPLOAD_FILE_NAME, UPLOAD_BUCKET_NAME, UPLOAD_S3_DIR)
    print(res)
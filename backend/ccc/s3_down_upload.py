# coding=gbk
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

        self.client = boto3.client(
            service_name='s3',
            region_name=self.region_name,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
        )

    def download_file_s3(self, bucket_name, file_name, local_file):
        """
        从s3下载指定文件到本地
        需要本地运行程序的目录下新建一个local_file完整目录
        :param bucket_name: 桶名称
        :param file_name: 要下载的文件，所在路径
        :return: 下载完成返回True，下载出问题返回False，并打印错误
        """

        bucket = self.s3.Bucket(bucket_name)

        for obj in bucket.objects.all():
            if obj.key == file_name:
                p = re.compile(r'.*/(.*)')
                result = p.search(file_name).group(1)

                down_file = local_file + result
                try:
                    bucket.download_file(file_name, down_file)
                    return True
                except Exception as e:
                    print('出错了：' + str(e))
                    return False

    def get_list_s3(self, bucket_name, file_name):
        """
        用来列举出该目录下的所有文件
        :param bucket_name: 桶名称
        :param file_name: 要查询的文件夹
        :return: 该目录下所有文件列表
        """
        # 用来存放文件列表
        file_list = []

        response = self.client.list_objects_v2(
            Bucket=bucket_name,
            Delimiter='/',
            Prefix=file_name,
        )

        for file in response['Contents']:
            s = str(file['Key'])
            p = re.compile(r'.*/(.*)(\..*)')
            if p.search(s):
                s1 = p.search(s).group(1)
                s2 = p.search(s).group(2)
                result = s1 + s2
                file_list.append(result)
        return file_list

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
        "ACCESS_KEY": "你自己的",
        "SECRET_KEY": "你自己的",
        "REGION_NAME": "你自己的",

        "DOWN_BUCKET_NAME": "桶的名称",
        "DOWN_FILE_NAME": "需要下载的s3的文件目录",
        "DOWN_LOCAL_FILE": "你本地的目录",

        "GET_BUCKET_NAME": "桶的名称",
        "GET_FILE_NAME": "需要列表的目录",

        "UPLOAD_FILE_NAME": "你本地要上传的文件",
        "UPLOAD_BUCKET_NAME": "桶的名称",
        "UPLOAD_S3_DIR": "s3需要上传的目录",
    }
    s3 = S3Helper()
    res = s3.download_file_s3(S3_FILE_CONF["DOWN_BUCKET_NAME"], S3_FILE_CONF["DOWN_FILE_NAME"], S3_FILE_CONF["DOWN_LOCAL_FILE"])
    print(res)
    file_list = s3.get_list_s3(S3_FILE_CONF["GET_BUCKET_NAME"], S3_FILE_CONF["GET_FILE_NAME"])
    print(file_list)
    res = s3.upload_file_s3(S3_FILE_CONF["UPLOAD_FILE_NAME"], S3_FILE_CONF["UPLOAD_BUCKET_NAME"], S3_FILE_CONF["UPLOAD_S3_DIR"])
    print(res)
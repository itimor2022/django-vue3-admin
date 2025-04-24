# coding=gbk
import boto3
import re
import sys


class S3Helper(object):
    """
    ��Ҫ����boto3ģ��
    """

    def __init__(self):
        self.access_key = S3_FILE_CONF.get("ACCESS_KEY")
        self.secret_key = S3_FILE_CONF.get("SECRET_KEY")
        self.region_name = S3_FILE_CONF.get("REGION_NAME")

        # ����s3
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
        ��s3����ָ���ļ�������
        ��Ҫ�������г����Ŀ¼���½�һ��local_file����Ŀ¼
        :param bucket_name: Ͱ����
        :param file_name: Ҫ���ص��ļ�������·��
        :return: ������ɷ���True�����س����ⷵ��False������ӡ����
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
                    print('�����ˣ�' + str(e))
                    return False

    def get_list_s3(self, bucket_name, file_name):
        """
        �����оٳ���Ŀ¼�µ������ļ�
        :param bucket_name: Ͱ����
        :param file_name: Ҫ��ѯ���ļ���
        :return: ��Ŀ¼�������ļ��б�
        """
        # ��������ļ��б�
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
        �ϴ������ļ���s3ָ���ļ�����
        :param file_name: �����ļ�·��
        :param bucket: Ͱ����
        :param s3_dir:Ҫ�ϴ�����s3�ļ�������
        :return: �ϴ��ɹ�����True���ϴ�ʧ�ܷ���False������ӡ����
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
            print('�����ˣ�' + str(e))
            return False
        return True


if __name__ == '__main__':
    S3_FILE_CONF = {
        "ACCESS_KEY": "���Լ���",
        "SECRET_KEY": "���Լ���",
        "REGION_NAME": "���Լ���",

        "DOWN_BUCKET_NAME": "Ͱ������",
        "DOWN_FILE_NAME": "��Ҫ���ص�s3���ļ�Ŀ¼",
        "DOWN_LOCAL_FILE": "�㱾�ص�Ŀ¼",

        "GET_BUCKET_NAME": "Ͱ������",
        "GET_FILE_NAME": "��Ҫ�б��Ŀ¼",

        "UPLOAD_FILE_NAME": "�㱾��Ҫ�ϴ����ļ�",
        "UPLOAD_BUCKET_NAME": "Ͱ������",
        "UPLOAD_S3_DIR": "s3��Ҫ�ϴ���Ŀ¼",
    }
    s3 = S3Helper()
    res = s3.download_file_s3(S3_FILE_CONF["DOWN_BUCKET_NAME"], S3_FILE_CONF["DOWN_FILE_NAME"], S3_FILE_CONF["DOWN_LOCAL_FILE"])
    print(res)
    file_list = s3.get_list_s3(S3_FILE_CONF["GET_BUCKET_NAME"], S3_FILE_CONF["GET_FILE_NAME"])
    print(file_list)
    res = s3.upload_file_s3(S3_FILE_CONF["UPLOAD_FILE_NAME"], S3_FILE_CONF["UPLOAD_BUCKET_NAME"], S3_FILE_CONF["UPLOAD_S3_DIR"])
    print(res)
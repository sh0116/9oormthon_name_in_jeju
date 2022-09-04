FROM amazon/aws-lambda-python:3.8

RUN /var/lang/bin/python3.8 -m pip install --upgrade pip
RUN yum install git -y
RUN git clone https://github.com/sh0116/9oornthoon_name_in_jeju.git
RUN pip install -r 9oornthoon_name_in_jeju/requirements.txt
RUN cp 9oornthoon_name_in_jeju/lambda_function.py /var/task/
RUN cp -r 9oornthoon_name_in_jeju/model/ /var/task/

CMD ["lambda_function.handler"]

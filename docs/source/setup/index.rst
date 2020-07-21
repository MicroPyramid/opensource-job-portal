Configuration of Peeljobs
=========================

1. Create a directory using mkdir peeljobs, move to it using cd

   .. code-block:: python

		mkdir peeljobs
		cd peeljobs

2. Install virtualenv in your local using following command

   .. code-block:: python

		sudo apt-get install virtualenv

3. Create an env in your project dir and activate using following.

   .. code-block:: python

		virtualenv -p python3 env
		source ../env/bin/activate

4. Again create another peeljobs directory for clonning the project.

   .. code-block:: python

		mkdir peeljobs
		cd peeljobs

5. Make sure git installed in your machine or else install by following below command.

   .. code-block:: python

		sudo apt-get install git


   .. code-block:: python

		git config --user.email <your email id>
		git config --user.name  <your name>

6. Then intialize the git by using the following command

   .. code-block:: python

   		git init


7. Include peeljobs repository using following command.

   .. code-block:: python

		git remote add origin https://github.com/MicroPyramid/opensource-job-portal.git

7. Pull the code of peeljobs using following command

   .. code-block:: python

		git pull origin master

8. Install requirements, node and sass using following

   .. code-block:: python

		sudo apt install curl
		curl -sL https://deb.nodesource.com/setup_10.x | sudo -E bash -
		sudo apt-get update
		sudo apt install nodejs
		npm install -g sass
		pip install -r requirements.txt


9. We used postgressql here open shell and create the following database
	
   .. code-block:: python

		sudo su - postgres
		psql
		create database peeldb;

10. We have to use third party related keys. We have to had those keys in order to run the application.

		**Sendgrid details**

		SG_USER=<sendgrid username>
		
		SG_PWD=<sendgrid password>
		
		**Google developers account details**

		GP_CLIENT_ID=<oauth0 client id>

		GP_CLIENT_SECRET=<oauth0 client secret-key>
		
		ENABLE_GOOGLE_LOGIN=<variable to configure google login in application>

		**Facebook details**

		FB_APP_ID = <facebook access key id>
		
		FB_SECRET = <facebook access secret-key>

		**Aws account details**

		AWSBUCKETNAME = <aws bucket name>
		
		AWS_ACCESS_KEY_ID = <aws access key id>
		
		AWS_SECRET_ACCESS_KEY = <aws access secret-key>

		**Git account details**

		GIT_APP_ID = <git api id>
		
		GIT_APP_SECRET = <git secret-key>

		**LinkedIn account details**

		LN_API_KEY = <linkedin api id>

		LN_SECRET_KEY = <linkedin secret-key>

		**Mailgun accout details**

		MGUN_API_URL = <mailgun api url>

		MGUN_API_KEY = <mailgun api secret-key>



11. Apply migrations to database using the following command

    .. code-block:: python

		python manage.py migrate


12. Now run application using following command, and visit http://localhost:8000

    .. code-block:: python

		python manage.py runserver


14. We’re using celery for sending emails, other related tasks in the application. Run celery using
    the following commands

    .. code-block:: python

      celery -A peeljobs worker -l info

      celery -A peeljobs beat -l info
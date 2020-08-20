1. install packages from requirements
2. load sample data
3. run elasticsearch with the following command
docker run -d --name elasticsearch -p 9200:9200 -p 9300:9300 -e "discovery.type=single-node" elasticsearch:2.4
4. then you should be good to go and explore
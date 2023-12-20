from flask import Flask,render_template, request, jsonify
import requests
from requests import get, post

app = Flask('app')
@app.route('/ffs.php',methods=['GET','POST'])
def bard_ai():
  if request.method == 'GET':
    token = 'EAAD6V7os0gcBO5ai7IF9fmkh2cYX7zYwdsnkaQ7Fb6d9CU9r6wGVDljdOXB6bBgsTmAkpkFZC6E1zz0ZA2d5JET90HKNBcywo4PKSpD469RZA1WOrkTOsUALqXt0tT5VEODdC2jXcVDaC5ZCkTIzdKwiSQ8Avzt8H11EHYfZARMu1buTLFKAZAvYJnwOYMs0ZCGwwZDZD.'
    ques = request.args.get('chat')
    site=requests.get(f"https://graph.facebook.com/{ques}?fields=subscribers.limit(0)&access_token={token}").json()
    json1 = jsonify(followers=site['subscribers']['summary']['total_count'])
    return json1
    
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8080)
def keep_alive():
  t=Thread(target=run)
  t.start()
keep_alive()

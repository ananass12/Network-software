from flask import Flask, render_template_string, request, jsonify
import sys
sys.path.insert(0, '.')
from client import GraphQLClient, build_payload

app = Flask(__name__)
graphql = GraphQLClient(endpoint="http://nginx/graphql")  

HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>GraphQL Client</title>
    <style>
        body { font-family: monospace; max-width: 1200px; margin: 20px auto; padding: 0 20px; }
        textarea { width: 100%; min-height: 150px; font-family: monospace; }
        .row { display: flex; gap: 20px; margin: 10px 0; }
        .col { flex: 1; }
        button { padding: 10px 20px; background: #007bff; color: white; border: none; cursor: pointer; }
        button:hover { background: #0056b3; }
        #output { background: #f4f4f4; padding: 15px; border-radius: 5px; white-space: pre-wrap; }
        .error { color: #dc3545; }
        .success { color: #28a745; }
    </style>
</head>
<body>
    <h1>GraphQL Client</h1>
    
    <div class="row">
        <div class="col">
            <label><strong>Query / Mutation:</strong></label>
            <textarea id="query" placeholder="query { getAllTickets { id status } }"></textarea>
        </div>
        <div class="col">
            <label><strong>Variables (JSON):</strong></label>
            <textarea id="variables" placeholder='{"status": "high"}'></textarea>
        </div>
    </div>
    
    <button onclick="execute()">Выполнить</button>
    <button onclick="fillGetAll()">Загрузить все билеты</button>
    <button onclick="fillCreate()">Создать билет</button>
    
    <h3>Ответ:</h3>
    <div id="output">Нажмите "Выполнить" для отправки запроса...</div>

    <script>
        async function execute() {
            const query = document.getElementById('query').value;
            let variables = document.getElementById('variables').value.trim();
            
            // Парсим variables, если есть
            let varsObj = {};
            if (variables) {
                try { varsObj = JSON.parse(variables); }
                catch(e) { return showOutput('Ошибка JSON в variables: ' + e, 'error'); }
            }
            
            const output = document.getElementById('output');
            output.textContent = 'Загрузка...';
            
            try {
                const res = await fetch('/api/graphql', {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({query, variables: varsObj})
                });
                const data = await res.json();
                
                if (data.errors) {
                    showOutput('Ошибки:\\n' + JSON.stringify(data.errors, null, 2), 'error');
                } else {
                    showOutput('Данные:\\n' + JSON.stringify(data.data, null, 2), 'success');
                }
            } catch(e) {
                showOutput('Сетевая ошибка: ' + e, 'error');
            }
        }
        
        function showOutput(text, cls) {
            const el = document.getElementById('output');
            el.textContent = text;
            el.className = cls;
        }
        
        function fillGetAll() {
            document.getElementById('query').value = `query {
  getAllTickets { 
    id 
    status 
  }
}`;
            document.getElementById('variables').value = '';
        }
        
        function fillCreate() {
            document.getElementById('query').value = `mutation CreateTicket($status: String!) {
  createTicket(input: {status: $status}) { 
    id 
    status 
  }
}`;
            document.getElementById('variables').value = '{"status": "high priority"}';
        }
    </script>
</body>
</html>
"""

@app.route('/')
def index():
    return render_template_string(HTML_TEMPLATE)

@app.route('/api/graphql', methods=['POST'])
def proxy_graphql():
    """Прокси для GraphQL-запросов"""
    data = request.get_json()
    query = data.get('query', '')
    variables = data.get('variables', {})
    
    try:
        result = graphql.execute(query, variables)
        return jsonify(result)
    except Exception as e:
        return jsonify({"errors": [{"message": str(e)}]}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
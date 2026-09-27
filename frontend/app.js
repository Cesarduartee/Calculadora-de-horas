const api = "http://127.0.0.1:5000";

async function calcular() {
    const inicio = document.getElementById("inicio").value;
    const duracao = document.querySelector('input[name="duracao"]:checked').value;

    if (!inicio) {
        alert("Informe a hora de início");
        return;
    }

    const resposta = await fetch(api + "/calculos", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({inicio, duracao})
    });

    const dados = await resposta.json();
    document.getElementById("saida").textContent = dados.saida;
    listar();
}

async function listar() {
    const resposta = await fetch(api + "/calculos");
    const dados = await resposta.json();
    const historico = document.getElementById("historico");
    historico.innerHTML = "";

    dados.forEach(item => {
        historico.innerHTML += `
            <div class="item">
                ${item.inicio} + ${item.duracao} = ${item.saida}
                <button onclick="ver(${item.id})">Ver</button>
                <button onclick="excluir(${item.id})">Excluir</button>
            </div>`;
    });
}

async function ver(id) {
    const resposta = await fetch(api + "/calculos/" + id);
    const item = await resposta.json();
    alert("Início: " + item.inicio + "\nDuração: " + item.duracao + "\nSaída: " + item.saida);
}

async function excluir(id) {
    await fetch(api + "/calculos/" + id, {method: "DELETE"});
    listar();
}

listar();

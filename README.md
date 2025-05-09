# Desafio Técnico – Desenvolvedor(a) Back-end Sênior

Bem-vindo(a) a implantação do Desafio Técnico - Desenvolvedor(a) Back-end Sênior.

Nesse README, você encontrará detalhes de como rodar o código, testá-lo, além de detalhes de funcionamento e implantação

## Como rodar

Primeiro, tenha o **docker compose** instalado. Para garantir que tudo funcione conforme no meu ambiente, é ideal que se tenha a versão **v2.35.1**

Com isso, use o seguinte comando para levantar os containers (privilégios podem ser necessários para rodar comandos docker):

```console
docker compose up --build
```

E pronto, o serviço já está rodando na porta **8000**. Para acessá-lo, basta entrar em localhost:8000, seguido de um dos caminhos. O mais útil para teste e documentação. é o [/docs](http://localhost:8000/docs)

## Como usar

O endpoint [/docs](http://localhost:8000/docs) é uma documentação utilizando OpenAPI, que mostra os endpoints agrupados em categorias, juntamente com descrições e maneiras de usá-los sem a necessidade de ferramenteas externas como Postman.

As funcionalidades esstão suficientemente documentadas no próprio endpoint descrito acima, mas aqui vai uma breve descrição por completude:

- A categoria **Public** agrupa os endpoints que podem ser acessados por qualquer um e que não tem ligação com autenticação. Nela, só existe o endpoint de saúde, que verifica se o serviço está online.

- A categoria **Auth** agrupa os endpoints de autenticação. Nela, é possível registrar um usuário e fazer login. Note que existe o login normal e um login para a implementação de autenticação em dois fatores. Seu funcionamento será melhor discutida na parte de decisões deste documento

- A categoria **User** apresenta os endpoints que somente um usuário autenticado pode utilizar. Nela, temos funções como conversar com o chatbot, operar sobre o saldo do passe de transporte e sobre os documentos do usuário

Para acessar esta última categoria, pode-se clicar no cadeado presente na documentação, colocando um email e uma senha já registradas pelo endpoint de registro. Note que para utilizar os endpoints de dois fatores, é necessário o uso de uma ferramenta externa como Postman. Mais detalhes na parte de decisões.


## Como testar executar testes automatizados

Os testes são executados automaticamente por meio de **Github Actions** toda vez que há um **push** ou um **pull_request** no repositório do Github. As especificações deste workflow se encontram no arquivo [test-workflow.yml](.github/workflows/test-workflow.yml). 

Se precisar rodar os testes "manualmente", use o **docker compose** normalmente para subir os containers e use o seguinte comando para ver os containers rodando:

```console
docker ps
```

Com isso, ache o id do container que usa a imagem **desafio-senior-backend-developer-api**. Após isso, com seu id, rode

```console
docker exec -it SEU_ID bash
```

para "entrar" no container. Agora simplesmente pode-se usar:

```console
pytest
```

e pronto! Os testes são executados!

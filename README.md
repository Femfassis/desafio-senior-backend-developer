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

O endpoint [/docs](http://localhost:8000/docs) é uma documentação utilizando OpenAPI, que mostra os endpoints agrupados em categorias, juntamente com descrições e maneiras de usá-los sem a necessidade de ferramentas externas como Postman.

As funcionalidades esstão suficientemente documentadas no próprio endpoint descrito acima, mas aqui vai uma breve descrição por completude:

- A categoria **Public** agrupa os endpoints que podem ser acessados por qualquer um e que não tem ligação com autenticação. Nela, só existe o endpoint de saúde, que verifica se o serviço está online.

- A categoria **Auth** agrupa os endpoints de autenticação. Nela, é possível registrar um usuário e fazer login. Note que existe o login normal e um login para a implementação de autenticação em dois fatores. Seu funcionamento será melhor discutida na parte de decisões deste documento

- A categoria **User** apresenta os endpoints que somente um usuário autenticado pode utilizar. Nela, temos funções como conversar com o chatbot, operar sobre o saldo do passe de transporte e sobre os documentos do usuário

Para acessar esta última categoria, pode-se clicar no cadeado presente na documentação, colocando um email e uma senha já registradas pelo endpoint de registro. Note que para utilizar os endpoints de dois fatores, é necessário o uso de uma ferramenta externa como Postman. Mais detalhes na parte de [decisões](#mfa).


## Como executar testes automatizados

Os testes são executados automaticamente por meio de **Github Actions** toda vez que há um **push** ou um **pull_request** no repositório do Github. As especificações deste workflow se encontram no arquivo [test-workflow.yml](.github/workflows/test-workflow.yml). 

Se precisar rodar os testes "manualmente", use o **docker compose** normalmente para subir os containers e use o seguinte comando para ver os containers rodando:

```console
docker ps
```

Com isso, ache o id do container que usa a imagem **desafio-senior-backend-developer-api**. Após isso, com seu id, rode

```console
docker exec -it SEU_ID pytest
```

e pronto! Os testes são executados!


## Decisões de projeto

Nesta seção, estão descritas as decisões de implementação e estrutura do projeto.

### Banco de dados

O banco de dados escolhido foi o Postgresl, juntamente com o SQLAlchemy como ORM, ambos por simplicidade.

Os scripts relacionados a banco de dados estão na pasta [db](api/db/). Como o projeto é relativamente simples, todos os modelos estão no mesmo arquivo [models.py](api/db/models.py). Para um projeto maior, poderia ser interessante separar em múltiplos arquivos.

Existem 3 modelos: **User**, **Transport** e **Document**

- **User** é o modelo mais importante, representando o usuário do sistema. Ele é basicamente representado pelo email, mas também tem campos para senha, id e um token especial, além de relações com as entidades de transporte e documento. Apesar do email ser único, foi escolhido fazer um campo único para id por dois motivos: uma pessoa pode querer mudar email, fazendo-o ser contra indicado para chave primária. Além disso, é mais fácil fazer operações como de comparação com um inteiro do que como uma string. O token especial se trata de um token temporário para verificação de duas etapas.

- **Transport** é o modelo ligado ao saldo do passe de transporte do usuário. Em teoria, poderia ser apenas um atributo do modelo do usuário, mas foi escolhido criar uma entidade própria para facilitar sua expansão e evitar um acoplamento desnecessário com o usuário. A relação entre os dois é de 1 para 1. O saldo foi escolhido como do tipo float para simplicidade de apresentação aos avaliadores do projeto, mas em um ambiente real, seria interessante usar um número inteiro (o valor em centavos). Isso porque aritimética de ponto flutuante pode resultar em imprecisões. Estas imprecisões foram corrigidas em tempo de execução, como será visto em outra seção.

- **Document** é o modelo ligado aos diversos documentos que o usuário pode ter. O documento é bascimente representado por seu número, tendo também um nome (sendo esse o nome do Documento e não do usuário. Por exemplo, nome pode ser "CPF", "RG", etc). Note que os requisitos não apresentam muito detalhes sobre a natureza dos documentos, por isso a simplicidade na implementação. Para um caso real, com mais requisitos, esta classe pode ser estendida por meio de heranças, para os mais diversos tipos de documentos, com validações para cada tipo. A relação com o usuário é de muitos para 1, ou seja, um usuário pode ter vários documentos, mas cada documento tem apenas um usuário.

### Variáveis de ambiente

As variáveis de ambiente, que são de caráter sensível, são armazenadas na [.env](.env). Nos scripts python, são lidas por meio da python-decouple.

Note que normalmente este arquivo não estaria presente aqui junto ao resto no repositório, pois é uma variável local de conteúdo sensível, como a chave privada. Porém, é necessária para mostrar o funcionamento do projeto. Numa situação real, este arquivo estaria no [.gitignore](.gitignore).

### Arquivo de inicialização

Para questões de sincronização e de maior flexibilidade, foi criado um arquivo [start_api.sh](start_api.sh) que roda comandos básicos após a iniciação do container. Suas tarefas são esperar um pequeno delay para a iniciação do banco de dados, garantir as migrações com **Alembic** e iniciar a api com **Uvicorn**.

### Versões

Como isso se trata apenas de um teste, não foram escolhidas versões específicas para as bibliotecas utilizadas, sendo pegas as mais recentes. Em um ambiente real, o melhor seria especificar as versões para impedir qualquer versão de compatibilidade devido a atualizações surpresas.

### Casos de uso

As funcionalidades principais foram separadas em casos de uso, para assim liberar o código dos endpoints livre de "trabalho pesado", deixando as coisas mais organizadas.

A classe presente no arquivo [auth.py](api/cases/auth.py) é responsável pelos casos de uso de registro e log in, utilizando métodos criptográficos para hash de senhas com sal e sua verificação. Além disso, é aqui que os tokens de acesso são validádos.

Além disso, essa classe também é responsável pela validação em duas etapas, porém os comentários sobre ela estão em outra [seção](#mfa).

Já em [user.py](api/cases/user.py) estão os casos de uso para o usuário já autenticado. Nesta classe, são trabalhados os documentos do usuário. As outras funcionalidades que dependem do usuário estar autenticado são tratadas diretamente nos código para os endpoints em si, como será visto a seguir. Isso ocorre pois as funcionalidades são bem simples.

### Rotas

As rotas são tratadas em dois arquivos: [main.py](api/main.py) e [routes.py](api/routes.py). 

O primeiro, se trata do arquivo principal do código e nele só está a funcionalidade mais básica, a verificação de saúde da api.

Já no segundo, estão o restante das rotas. Elas estão separadas em categorias por meio de comentários, mas poderiam também estar em arquivos diferentes.

Nas rotas de login, as funções basicamente trabalham com as funções de caso de uso e dão a resposta HTTP adequada.

Nas rotas de usuário, temos as rotas de documento e as demais. As de documento usam os casos de uso do usuário como dito anteriormente. As demais, são simples o suficiente para terem sua lógica implementada diretamente.

Um detalhe especial para o caso de recarga, que tem uma pequena correção de valores em ponto flutuante. Por exemplo, em Python, 0.4+0.2=0.6000000000000001. Por isso, certa lógica tem que ser implementada para os números somarem corretamente e se manterem com duas casas decimais. Como dito anteriormente, isso poderia ser evitado mais facilmente se o saldo fosse guardado como um número inteiro, isto é, em centavos.


### Testes

Os testes são encontrados no diretório [tests](tests) e separados em quatro arquivos que representam o arquivo principal os quais eles testam.

Os principais são os arquivos que testam os casos de uso, pois esses são o que representam as funcionalidades principais do sistema. Esses testes pegam as funções das classes de caso de uso e testam todos os caminhos principais que elas podem passar, com a situação explicitada no nome da função de teste. 

Além disso, há dois arquivos que são responsáveis por testes em algumas rotas, só pra demonstrar que é possível, mesmo não sendo funcionalidades críticas.

### A questão temporal

Datas em computadores podem causar problemas devido a coisas como fusos horários. Por isso, todas as datas estão no utc. 

### MFA

Neste trabalho, foi implementada uma autenticação de duas etapas como adicional. Na área de segurança, a autenticação pode depender de 3 coisas: o que você tem, o que você é e o que você sabe. Um exemplo de cada um pode ser: um smartphone, uma biometria e uma senha.

Para realizar de maneira prática, seria então necessário enviar algo a um objeto que o usuário tem ou coletar sua biometria, ambas as situações inviáveis para esta demonstração.

Então, o processo é realizado da seguinte forma:

Um endpoint recebe login e senha do usuário, criando assim um token especial e salvando esse token no banco. Em uma situação real, o token seria enviado ao usuário por uma forma alternativa, como para o email ou alguma aplicação de smartphone, por exemplo. No nosso caso, a aplicação envia o token na própria reposta do endpoint, para facilitar quem estiver testando.

O usuário, agora munido desse token, vai ao endpoint da segunda parte do login e coloca esse token juntamente ao seu email, para finalmente ser autenticado.

No mundo real, essa troca de endpoints seria feita por um fronted e o usuário não precisaria escrever seu email duas vezes, isso também seria responsabilidade do frontend.

O token funciona da seguinte forma: é um número aleatório de 6 digitos, concatenado a uma data de expiração. Se o usuário tentar entrar com um token de número diferente ou expirado, ele não consegue.

Para testar o token, você pode simplesmente seguir os passos ditos acima pelos endpoins de login parte um e login parte 2. Porém, diferentemente do login normal, não é possível clicar no ícone de cadeado para se manter autenticado. Porém, é possível utilizar o token de acesso dado pela parte final de login e utilizado diretamente, por exemplo por meio de uma ferramenta como Postman.
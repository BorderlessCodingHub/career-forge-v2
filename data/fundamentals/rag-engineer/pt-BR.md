---
goal_id: rag-engineer
locale: pt-BR
---

Um sistema de RAG em produção recupera passagens primeiro e só então pede ao modelo que responda a partir dessas passagens.

## Recupere antes de o modelo escrever

Um modelo que só lembra o treino responde com o que viu quando foi treinado. Essa memória envelhece e não aponta o documento em que se deve confiar. A geração aumentada por recuperação coloca um acervo de conteúdo antes da escrita. A pergunta chega ao acervo primeiro. O modelo então escreve com essas passagens no prompt, e não só de memória.

O acervo pode ser uma coleção fechada — políticas, runbooks, chamados, um corpus de produto — ou uma aberta, como a web pública. O contrato é o mesmo nos dois casos: a resposta só está tão atual quanto as passagens que foram recuperadas, e quem lê deve poder ver quais passagens foram usadas.

Duas falhas aparecem antes de qualquer truque de ranking. A primeira é responder sem fonte. A segunda é responder a partir de uma fonte que já não corresponde ao mundo. A recuperação é o passo que consulta o fato antes de a frase ser escrita.

## Trechos que o recuperador encontra

O recuperador não busca o corpus como um bloco único. Ele busca trechos: pedaços pequenos o bastante para ranquear e grandes o bastante para ainda dizer alguma coisa. Um trecho que separa uma definição da exceção dela recupera a definição e deixa a exceção de fora. Um trecho que cola três assuntos sem relação acerta a consulta em um assunto e arrasta os outros dois para o prompt.

Um trecho útil guarda uma afirmação, a condição que a limita e palavras vizinhas suficientes para a afirmação ainda fazer sentido sozinha. A sobreposição entre trechos vizinhos existe para que uma frase na fronteira não seja a única cópia. O embedding, quando se usa um, tem de ser o mesmo modelo e a mesma dimensão na consulta e em cada trecho guardado. Misturar mapas faz "perto" perder o sentido.

A busca lexical ainda cabe quando a consulta cita um identificador, um código de erro ou um termo de produto que o embedding nunca foi treinado para tratar como especial. Muitos sistemas em produção rodam as duas buscas e fundem as listas. A regra de fusão faz parte do sistema; não é um detalhe para inventar na hora de ler.

## Responda a partir das passagens

O prompt que chega ao modelo tem três tarefas. Diz para responder a partir das passagens recuperadas. Inclui essas passagens. Inclui a pergunta. Se as passagens não contêm a resposta, o modelo deve dizer isso. Um parágrafo fluente que ignora as passagens é a falha que a recuperação foi posta para evitar.

A citação fica ao lado da afirmação que ela sustenta. Um link para o corpus inteiro não é citação. Quem lê, e qualquer checagem depois, precisa da passagem. Quando duas passagens discordam, a resposta deve mostrar o desacordo em vez de tirar uma média e inventar um terceiro fato que nenhuma fonte afirmou.

O ajuste da geração não conserta uma recuperação ruim. Uma temperatura mais baixa deixa a redação mais estável. Ela não põe de volta no prompt uma passagem que faltou. Quando a resposta está errada, olhe o que foi recuperado antes de olhar como o modelo foi amostrado.

## Observe o ciclo de recuperação

Marina Danilevsky, na IBM Research, percorre o mesmo ciclo: um modelo que responde pela memória de treino e, depois, a mesma pergunta com o acervo consultado primeiro. O vídeo é a versão curta de por que a consulta acontece antes da escrita.

https://www.youtube.com/watch?v=T-D1OfcDW1M

## Saiba quando a resposta não se sustenta

Trate uma execução como sem sustentação quando as passagens recuperadas não afirmam a tese, quando afirmam outra, ou quando o acervo que deveria ter o fato não devolveu nada. Registrar a pergunta, os ids dos trechos e a resposta é o registro mínimo. Sem isso, uma resposta errada não se rastreia até um trecho ruim, um índice velho ou um modelo que ignorou o prompt.

Trocar o embedding é uma migração de índice. Mudar o modelo de embedding, a dimensão ou a regra de trechos faz os vetores guardados deixarem de compartilhar um mapa com as consultas novas. Entregue isso como uma reconstrução, com um jeito de comparar o ranking antigo e o novo em perguntas em que você já confia.

O guia permanece o mesmo para toda pessoa neste objetivo. Uma trilha montada depois é um caminho pessoal pelas habilidades. Ela não reescreve esta leitura.

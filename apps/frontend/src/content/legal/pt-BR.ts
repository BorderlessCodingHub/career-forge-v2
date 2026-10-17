import { link, list, para } from "./blocks";
import type { LegalPack } from "./types";

const privacyLink = link("/legal/privacy", "Política de privacidade");
const contact = link("mailto:careerforgelabs@gmail.com", "careerforgelabs@gmail.com");

export const ptLegal: LegalPack = {
  navLabel: "Documentos legais",
  welcomeLabel: "Bem-vindo",
  nav: {
    privacy: "Política de privacidade",
    terms: "Termos de serviço",
    security: "Segurança",
  },
  pages: {
    terms: {
      title: "Termos de serviço",
      description:
        "Termos de serviço do Career Forge, operado pela Borderless Coding LLC.",
      updated: "Vigência: 17 de outubro de 2026. Última atualização: 17 de outubro de 2026.",
      sections: [
        {
          id: "agreement",
          heading: "Acordo",
          blocks: [
            para(
              'Estes Termos de serviço ("Termos") são um acordo entre você ("Cliente", "você") e a Borderless Coding LLC, uma sociedade de responsabilidade limitada do Wyoming, com endereço em 30 N Gould St, STE R, Sheridan, WY 82801, USA ("Borderless Coding", "nós"). Ao criar uma conta no Career Forge ou acessar o Career Forge, você aceita estes Termos por inteiro. Se não concordar, não use o Career Forge.',
            ),
          ],
        },
        {
          id: "services",
          heading: "1. Serviços",
          blocks: [
            para(
              "A Borderless Coding opera o Career Forge, um sistema de aprendizado adaptativo online. O Career Forge inclui:",
            ),
            list(
              "Uma entrevista de diagnóstico que mapeia onde você está antes de a trilha ser forjada.",
              "Um forge de trilha ao vivo para uma de quatro trilhas de LLM: engenheiro de RAG, engenheiro de agentes, evals de LLM e fine-tuning.",
              "Uma trilha que você segue.",
              "Validação de domínio.",
              "Um mentor contextual e um relatório de evidências.",
            ),
            para(
              "O Career Forge é entregue online. Nada físico é enviado. O Career Forge é o produto descrito nestes Termos.",
            ),
          ],
        },
        {
          id: "eligibility",
          heading: "2. Elegibilidade",
          blocks: [
            para(
              "Você precisa ter pelo menos 18 anos para criar uma conta ou usar o Career Forge. Ao criar uma conta, você confirma que as informações fornecidas são corretas e completas.",
            ),
          ],
        },
        {
          id: "account",
          heading: "3. Conta e acesso",
          blocks: [
            para(
              "Você entra com uma senha do Career Forge ou com uma conta Borderless. As credenciais são pessoais e intransferíveis. Você responde pela atividade na sua conta. Podemos suspender ou encerrar uma conta que viole estes Termos.",
            ),
          ],
        },
        {
          id: "delivery",
          heading: "4. Entrega",
          blocks: [
            para(
              "O Career Forge roda no produto: diagnóstico, forge, trilha e validação de domínio. O primeiro forge em uma conta externa está incluído. BASE e PSP não são cobrados pelo Career Forge. Depois desse forge incluído, o acesso pago segue o status da assinatura.",
            ),
          ],
        },
        {
          id: "payment",
          heading: "5. Pagamento",
          blocks: [
            para(
              "A assinatura externa é de USD $7/mês via Stripe. BASE e PSP não são cobrados pelo Career Forge. Os números de cartão são tratados pela Stripe e não são armazenados pelo Career Forge. Um pagamento recusado pode pausar o acesso pago até a assinatura ficar em dia.",
            ),
          ],
        },
        {
          id: "refund",
          heading: "6. Reembolso e cancelamento",
          blocks: [
            para("Esta seção é o texto de reembolso do Career Forge."),
            list(
              "A assinatura externa é de USD $7/mês via Stripe. BASE e PSP não são cobrados pelo Career Forge.",
              "O primeiro forge em uma conta externa está incluído.",
              "Valores já cobrados não são reembolsados. A janela de 7 dias das turmas da Borderless não se aplica.",
              "O cancelamento fica no portal de cliente da Stripe. O acesso pago segue o status da assinatura.",
            ),
          ],
        },
        {
          id: "ip",
          heading: "7. Propriedade intelectual",
          blocks: [
            para(
              "O software, os catálogos, a marca e os materiais do Career Forge que fornecemos são de propriedade da Borderless Coding LLC. Sua conta concede uma licença pessoal, intransferível e não exclusiva para usar o Career Forge no seu próprio aprendizado. Você não pode copiar, redistribuir, revender ou compartilhar esse material para uso comercial. Uma violação pode encerrar a conta. Valores já cobrados não são reembolsados, como diz a seção 6.",
            ),
          ],
        },
        {
          id: "conduct",
          heading: "8. Conduta",
          blocks: [
            para(
              "Você concorda em usar o Career Forge de forma lícita, em enviar apenas material que tem direito de fornecer e em não perturbar o serviço nem os dados de outros alunos. Podemos suspender o acesso por uma violação grave ou repetida. A suspensão não reembolsa valores já cobrados.",
            ),
          ],
        },
        {
          id: "disclaimer",
          heading: "9. Sem garantia de emprego",
          blocks: [
            para(
              "O Career Forge oferece aprendizado adaptativo. Não é um serviço de emprego, de recrutamento ou uma garantia de colocação. Os resultados dependem do seu esforço e de fatores que não controlamos. As histórias na página de marketing são resultados individuais. Não garantimos salário, oferta, entrevista ou prazo.",
            ),
          ],
        },
        {
          id: "liability",
          heading: "10. Limite de responsabilidade",
          blocks: [
            para("Na máxima extensão permitida pela lei:"),
            list(
              "A responsabilidade total da Borderless Coding por qualquer reclamação decorrente destes Termos ou do seu uso do Career Forge não excede o valor que você pagou à Borderless Coding pelo Career Forge nos doze meses anteriores à reclamação.",
              "Não respondemos por danos indiretos, incidentais, consequenciais ou punitivos, inclusive renda perdida, oportunidades perdidas ou resultados de carreira.",
              "Não respondemos por interrupções ou falhas de terceiros fora do nosso controle razoável.",
            ),
          ],
        },
        {
          id: "privacy",
          heading: "11. Privacidade",
          blocks: [
            para(
              "Seus dados pessoais são tratados conforme nossa ",
              privacyLink,
              ". Ao usar o Career Forge, você reconhece essa política.",
            ),
          ],
        },
        {
          id: "third-parties",
          heading: "12. Serviços de terceiros",
          blocks: [
            para(
              "O Career Forge usa a Stripe para cobrança, a Resend para e-mail e um provedor de modelo (OpenAI) para diagnóstico, forge e validação. O Sentry recebe relatórios de erro quando um DSN está definido. O LangSmith recebe rastros quando o rastreamento está ligado. Não respondemos pelos termos, pela disponibilidade ou pelas práticas de dados deles.",
            ),
          ],
        },
        {
          id: "modifications",
          heading: "13. Alterações",
          blocks: [
            para(
              "Podemos atualizar estes Termos. A data no topo desta página muda quando fazemos isso. Continuar usando o Career Forge depois de uma atualização é aceitar os Termos atualizados.",
            ),
          ],
        },
        {
          id: "law",
          heading: "14. Lei aplicável e disputas",
          blocks: [
            list(
              "Estes Termos são regidos pelas leis do Estado de Wyoming, Estados Unidos.",
              "Qualquer disputa é tratada primeiro de boa-fé pelo contato careerforgelabs@gmail.com.",
              "Se continuar sem resolução depois de 30 dias, segue para arbitragem vinculante sob as regras da American Arbitration Association, conduzida em inglês.",
              "Você renuncia ao direito de participar de uma ação coletiva ou de uma arbitragem coletiva.",
            ),
          ],
        },
        {
          id: "severability",
          heading: "15. Divisibilidade",
          blocks: [
            para(
              "Se alguma disposição destes Termos for considerada inexequível, as demais permanecem em pleno vigor.",
            ),
          ],
        },
        {
          id: "entire",
          heading: "16. Acordo integral",
          blocks: [
            para(
              "Estes Termos, inclusive a seção 6 como texto de reembolso, junto com a Política de privacidade, são o acordo integral entre você e a Borderless Coding LLC sobre o Career Forge.",
            ),
          ],
        },
        {
          id: "contact",
          heading: "Contato",
          blocks: [
            para("E-mail: ", contact),
            para("Entidade: Borderless Coding LLC"),
            para("Endereço: 30 N Gould St, STE R, Sheridan, WY 82801, USA"),
          ],
        },
      ],
    },
    privacy: {
      title: "Política de privacidade",
      description:
        "O que o Career Forge guarda sobre conta, cobrança, aprendizado e navegador, e quais processadores usa.",
      updated: "Última atualização: 17 de outubro de 2026.",
      sections: [
        {
          id: "intro",
          heading: "1. Introdução",
          blocks: [
            para(
              'A Borderless Coding LLC ("Borderless Coding", "nós"), com endereço em 30 N Gould St, STE R, Sheridan, WY 82801, USA, opera o Career Forge. Esta política nomeia o que o Career Forge guarda e quais processadores tratam esses dados. Você precisa ter pelo menos 18 anos para usar o Career Forge.',
            ),
          ],
        },
        {
          id: "account",
          heading: "2. Conta",
          blocks: [
            para("Quando você cria uma conta, o Career Forge guarda:"),
            list(
              "Nome.",
              "E-mail.",
              "Hash da senha.",
              "Idioma.",
              "O vínculo com a conta Borderless, quando você entra com uma conta Borderless.",
            ),
            para("O Career Forge guarda o hash da senha, não a senha em si."),
          ],
        },
        {
          id: "billing",
          heading: "3. Cobrança",
          blocks: [
            para(
              "Para uma assinatura externa, o Career Forge guarda o identificador de cliente da Stripe e o identificador de assinatura da Stripe. Os números de cartão permanecem na Stripe. O Career Forge não armazena números de cartão.",
            ),
          ],
        },
        {
          id: "learning",
          heading: "4. Aprendizado",
          blocks: [
            para("O Career Forge guarda os registros de aprendizado que você cria no produto:"),
            list(
              "A entrevista de diagnóstico.",
              "O texto do CV em PDF, quando você envia um CV.",
              "A trilha.",
              "As respostas de validação.",
            ),
          ],
        },
        {
          id: "browser",
          heading: "5. Navegador",
          blocks: [
            para(
              "O Career Forge guarda o idioma no cookie cf_locale. O token de acesso do aluno fica no localStorage do seu navegador.",
            ),
          ],
        },
        {
          id: "processors",
          heading: "6. Processadores",
          blocks: [
            para("O Career Forge usa estes processadores para operar o produto:"),
            list(
              "Stripe, para cobrança.",
              "Resend, para e-mail.",
              "O provedor de modelo (OpenAI), para diagnóstico, forge, validação e chamadas de modelo relacionadas.",
              "Sentry, quando um DSN está definido, para relatórios de erro.",
              "LangSmith, quando o rastreamento está ligado, para rastros dessas execuções de modelo.",
            ),
            para(
              "Compartilhamos dados pessoais com um processador para que ele faça esse trabalho. O Career Forge não vende dados pessoais.",
            ),
          ],
        },
        {
          id: "use",
          heading: "7. Como usamos",
          blocks: [
            para(
              "Usamos esses dados para criar e autenticar sua conta, rodar o diagnóstico e o forge, guardar sua trilha e as respostas de validação, cobrar uma assinatura externa pela Stripe e enviar e-mail de conta pela Resend.",
            ),
          ],
        },
        {
          id: "requests",
          heading: "8. Pedidos de privacidade",
          blocks: [
            para(
              "Para pedir acesso, correção ou exclusão de dados pessoais do Career Forge, escreva para ",
              contact,
              ".",
            ),
          ],
        },
        {
          id: "security",
          heading: "9. Segurança",
          blocks: [
            para(
              "O que afirmamos sobre a proteção do Career Forge está na página de ",
              link("/legal/security", "Segurança"),
              ". Nenhum método é completamente seguro.",
            ),
          ],
        },
        {
          id: "changes",
          heading: "10. Alterações",
          blocks: [
            para(
              "Podemos atualizar esta política. A data no topo desta página muda quando fazemos isso.",
            ),
          ],
        },
        {
          id: "contact",
          heading: "11. Contato",
          blocks: [
            para("Pedidos de privacidade: ", contact),
            para("Entidade: Borderless Coding LLC"),
            para("Endereço: 30 N Gould St, STE R, Sheridan, WY 82801, USA"),
          ],
        },
      ],
    },
    security: {
      title: "Segurança",
      description: "As afirmações de segurança que o Career Forge faz.",
      updated: "Última atualização: 17 de outubro de 2026.",
      sections: [
        {
          id: "claims",
          heading: "O que afirmamos",
          blocks: [
            para(
              "O Career Forge é operado pela Borderless Coding LLC, 30 N Gould St, STE R, Sheridan, WY 82801, USA. Esta página afirma apenas o seguinte:",
            ),
            list(
              "O Career Forge é servido por HTTPS em trânsito.",
              "As senhas são armazenadas como hashes.",
              "Os dados de cartão são tratados pela Stripe e não são armazenados pelo Career Forge.",
              "O acesso a dados de produção é limitado a operadores.",
              "Nenhum método é completamente seguro.",
            ),
            para("Como o Career Forge trata dados pessoais está descrito na ", privacyLink, "."),
            para("Dúvidas de segurança: ", contact),
          ],
        },
      ],
    },
  },
};

#  Copyright (c) 2022. Hexagoon. Criador: Fabricio Gatto Lourençone. Todos os direitos reservados.

from sqlalchemy import select, asc
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import joinedload
from starlette.responses import Response

from api.v1.autenticacao.endpoint.autenticacao_endpoints import AutenticacaoEndpoints
from api.v1.recursos.acoes_initiallizer import AcoesInitiallizer
from api.v1.recursos.basic_exceptions.sql_exceptions import SQLException
from api.v1.usuario.model.usuario_model import UsuarioOut
from banco_dados.sql_alchemy.configuracao.oracle.data_oracle import Usuario, Artigo
from templates.Jinja2 import create_templates

templates = create_templates()


class HTMLAcoes(AcoesInitiallizer):
    # declara o tipo do model
    # model:
    # data:

    def acao_1(self):
        """ use : [login_1] """

        self.handler.sucesso = templates.TemplateResponse(
            "login.html",
            {
                "request": self.handler.request
            }
        )

    def acao_2(self):
        """ use : [admin_1] """

        try:
            if data := self.handler \
                    .sessao \
                    .query(Usuario) \
                    .options(
                joinedload(
                    Usuario.criado_por
                ),
                joinedload(
                    Usuario.alterado_por
                ),
                joinedload(
                    Usuario.deletado_por
                ),
                joinedload(
                    Usuario.a_roles
                )
            ) \
                    .all():
                self.data = data

        except NoResultFound:
            raise SQLException('Não há objetos do tipo usuário.')

        perfis: Role = self.handler.sessao.query(Role).all()

        self.model: UsuarioOut = self.data

        html_response = templates.TemplateResponse(
            "usuarios.html",
            {
                "request": self.handler.request,
                "usuarios": self.data,
                "perfis": perfis
            }
        )

        token = AutenticacaoEndpoints.create_token(self.handler)

        headers = {'authorization': token.token}

        self.handler.sucesso = Response(content=html_response.body, headers=headers, media_type="text/html")

    def acao_3(self):
        """ use : [article_1] """

        select_query = select(Artigo).where((Artigo.id == self._id))

        self.data = self.handler.sessao.execute(select_query).scalar_one()

        # forma de se recuperar somente algumas colunas da tabela
        select_query = select(Artigo.id, Artigo.titulo).order_by(asc(Artigo.id))

        artigos = ''  # inicializa a variável
        if data := self.handler.sessao.execute(select_query).fetchall():
            artigos = [Artigo(id=a[0], titulo=a[1]) for a in data]

        self.handler.sucesso = templates.TemplateResponse(
            "artigos/artigo_individual.html",
            {
                "request": self.handler.request,
                "artigo": self.data,
                "artigos": artigos
            }
        )

    def acao_4(self):
        """ use : [articleAll_1]"""

        # forma de se recuperar somente algumas colunas da tabela
        select_query = select(Artigo.id, Artigo.titulo).order_by(asc(Artigo.id))

        if data := self.handler.sessao.execute(select_query).fetchall():
            self.data = [Artigo(id=a[0], titulo=a[1]) for a in data]

        # recupera o artigo 1, que será o artigo exibido na página principal
        select_query = select(Artigo).filter_by(id=1)

        artigo = self.handler.sessao.execute(select_query).scalar_one()

        self.handler.sucesso = templates.TemplateResponse(
            "artigos/landing_page_artigos.html",
            {
                "request": self.handler.request,
                "artigos": self.data,
                "artigo": artigo
            }
        )

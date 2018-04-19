import attr
from flask import Flask, render_template, request, jsonify, redirect
from liteup.schemes.all_schemes import all_schemes
from liteup.options import parser, parse_options
app = Flask(__name__)
app.secret_key = 'This is really unique and secret'
app.config['DEBUG'] = True
app.current_scheme = None
app.options = {}
options = parse_options()


def preview_url(SchemeCls):
    return "%s.png" % (SchemeCls.__name__.lower())


@attr.s
class ConfigOption:
    name = attr.ib()

    data_type = attr.ib()

    cur_value = attr.ib()
    choices = attr.ib()

    description = attr.ib()

    @classmethod
    def from_parser_action(cls, action):
        global options
        name = action.option_strings[-1][2:]
        choices = action.choices
        if not choices:
            # we should populate values manually.
            if action.type == int:
                choices = [0, 20, 40, 60, 80, 100]
            # TODO more here

        return cls(
            name=name,
            data_type=action.type,
            cur_value=getattr(options, name, None),
            choices=choices,
            description=action.help,
        )


@app.route('/')
def LiteupBase():
    scheme_names = [
        (cls.__name__, preview_url(cls)) for cls in all_schemes
        if cls.ui_select
    ]
    if app.current_scheme:
        cur_scheme_cls = [s for s in all_schemes
                          if s.__name__ == app.current_scheme][0]

        config_strings = set([f"--{name}"
                              for name in cur_scheme_cls.options_supported])
        config_options = [
            ConfigOption.from_parser_action(action) for action in parser._actions
            if config_strings.intersection(set(action.option_strings))]
    else:
        config_options = []

    return render_template('mainpage.html',
                           scheme_names=sorted(scheme_names),
                           current_scheme=app.current_scheme,
                           config_options=config_options)


@app.route('/config', methods=["POST"])
def ConfigChange():
    print(request.form)
    app.options.update(request.form.to_dict())
    scheme_name = request.form.get('scheme_name', None)
    if scheme_name:
        app.current_scheme = scheme_name

    return redirect("/")


@app.route('/config', methods=["GET"])
def ConfigAPI():
    print(app.options)
    return jsonify(app.options)


if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0")

import attr
from flask import Flask, render_template, request, jsonify, redirect
from liteup.schemes.all_schemes import all_schemes
from liteup.options import parser, parse_options
app = Flask(__name__)
app.secret_key = 'This is really unique and secret'
app.config['DEBUG'] = True
app.current_scheme = None
app.custom_options = {}
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

        return cls(
            name=name,
            data_type=action.type,
            cur_value=app.custom_options.get(name),
            choices=action.choices,
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
    app.custom_options.update(request.form.to_dict())
    new_scheme = request.form.get('scheme', None)
    if new_scheme:
        app.current_scheme = new_scheme

        # flush any custom options that are now unsupported
        cur_scheme_cls = [s for s in all_schemes
                          if s.__name__ == app.current_scheme][0]
        app.custom_options = {key: value

                              for key, value in app.custom_options.items()
                              if key in cur_scheme_cls.options_supported or
                              key == 'scheme'}

    return redirect("/")


@app.route('/config', methods=["GET"])
def ConfigAPI():
    print(app.custom_options)
    return jsonify(app.custom_options)


if __name__ == "__main__":

    app.run(debug=True, host="0.0.0.0")

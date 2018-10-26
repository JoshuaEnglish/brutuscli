from cefpython3 import cefpython as cef
import sys
import base64
import json

import brutus

HTML = """
<!DOCTYPE html>
<html>
<head>
    <title>Brutus DSL</title>
    <link rel="stylesheet" href="https://www.w3schools.com/w3css/4/w3.css">
    <script
        src="https://code.jquery.com/jquery-3.3.1.slim.min.js"
        integrity="sha256-3edrmyuQ0w65f8gfBsqowzjJe2iM6n0nKciPUp8y+7E="
        crossorigin="anonymous">
    </script>
</head>
<body>
<header class="w3-container w3-light-green">
    <h1 class="w3-large">Brutus DSL</h1>
</header>
<div class="w3-row">
    <div class="w3-col m4 l3 w3-pale-blue" id="machine_rules">
        <header class="w3-container w3-blue"><div>Machine Rules</div></header>
        <table id="machine_rules_table" class="w3-table w3-bordered w3-small">
        <thead><tr><th>Words</th><th>Function</th><th>Callable</th></tr></thead>
        <tbody id="machine_rules_body"></tbody>
        </table>
    </div>
    <div class="w3-col m8 l9 w3-pale-green" id="program">
        <header class="w3-container w3-green"><div>Program</div></header>
        <form id="program" class="w3-container">
        <label>Program Text</label>
        <textarea id="program_text" class="w3-input"></textarea>
        <input type="submit" value="Load Program"/>
        </form>
        <div class="w3-row">
            <div class="w3-quarter>
                <ul id="program_items" class="w3-ul w3-border"></ul>
            </div>
        </div>
    </div>
</div>
</body>
<script type="text/javascript">
function list_machine_rules($data) {
    $("#machine_rules_body").empty();
    stuff = $.parseJSON($data);
    $.each(stuff, function(idx, data) {
        var row = "<tr><td>"+data[0]+"</td><td>"
            +data[1]+"</td><td>"+data[2]+"</td></tr>";
        $("#machine_rules_body").append(row);
        })};

function list_program($data) {
    $("#program_items").empty();
    stuff = $.parseJSON($data);
    $.each(stuff, function(item) {
        var li = "<li>" + item + "</li>";
        $("#program_items").append(li);
        })};

$("#program").submit(function(event) {
    interface.feed_program($("#program_text").val());
    event.preventDefault();
});

$(document).ready(function() { interface.load_the_machine(); });
</script>
</html>
"""


def main():
    sys.excepthook = cef.ExceptHook
    cef.Initialize()
    browser = cef.CreateBrowserSync(
        url=html_to_data_uri(HTML),
        window_title="Brutus DSL")
    set_client_handlers(browser)
    set_javascript_bindings(browser)
    cef.MessageLoop()
    cef.Shutdown()


def html_to_data_uri(html):
    html = html.encode("utf-8", "replace")
    b64 = base64.b64encode(html).decode("utf-8", "replace")
    return "data:text/html;base64,{data}".format(data=b64)


def set_client_handlers(browser):
    client_handlers = [LoadHandler(), DisplayHandler()]
    for handler in client_handlers:
        browser.SetClientHandler(handler)


def set_javascript_bindings(browser):
    interface = Interface(browser)
    bindings = cef.JavascriptBindings(
        bindToFrames=False, bindToPopups=False)
    bindings.SetObject("interface", interface)
    browser.SetJavascriptBindings(bindings)


class GloabalHandler(object):
    def OnOfterCreated(self, browser, **_):
        pass


class LoadHandler(object):
    def OnLoadingStateChange(self, browser, is_loading, **_):
        pass


class DisplayHandler(object):
    pass


class Interface(object):
    def __init__(self, browser):
        self.browser = browser
        self.machine = brutus.BaseMachine()

    def load_the_machine(self):
        self.load_machine_rules()

    def load_machine_rules(self):
        stringified_rules = [(" | ".join(tokens),
                              str(name),
                              str(thing.__name__)
                              if thing is not None else "none")
                             for tokens, name, thing in self.machine.rules]
        self.browser.ExecuteFunction(
           "list_machine_rules", json.dumps(stringified_rules))

    def feed_program(self, program_text):
        self.machine.feed(program_text)
        print(self.machine.program)
        self.browser.ExecuteFunction(
            "list_program", json.dumps(self.machine.program))


if __name__ == '__main__':
    main()

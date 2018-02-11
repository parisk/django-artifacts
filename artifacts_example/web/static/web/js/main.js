import { Terminal } from 'xterm';
import * as fit from 'xterm/lib/addons/fit/fit';

Terminal.applyAddon(fit);


let term = new Terminal();

// Expose to window for debugging
window.term = term;

document.addEventListener('DOMContentLoaded', function() {
  term.open(document.getElementById('xterm-container'));
  term.fit();

  term.writeln('It Werks!');
});

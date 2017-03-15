function chordMaker(B, C) {
    var H = function(g) {
        g = g || {};
        var a = [],
            c = {
                cellWidth: 21,
                cellHeight: 25,
                dotDia: 19,
                nutHeight: 5,
                fontBaseline: 7,
                fontHeight: 16,
                barGirth: 2,
                barHeight: 9,
                padding: 5,
                minSpan: 4
            },
            b, u, v, x, D, y, z, w, A, E, q, r, k, m, F, G, B = function(a) {
                for (var d = (v - 1) * k, h = w ? 1 : 0, e = ""; h <= x; h++) e += " M" + f(q) + " " + f(r + h * m) + " h" + f(d);
                a.setAttributeNS(null, "d", e)
            },
            C = function(a) {
                for (var d = f(x * m), h = 0, e = ""; h < v; h++) e += " M" + f(q + h * k) + " " + f(r) + " v" + d;
                a.setAttributeNS(null, "d", e)
            },
            H = function(a, d, h, e) {
                for (var l = 0, n = q; l < h.length; l++, n +=
                    k)
                    if (0 < h[l]) {
                        var p = document.createElementNS("http://www.w3.org/2000/svg", "circle"),
                            t = f(r + (h[l] - (w ? .5 : b - .5)) * m);
                        p.cx.baseVal.value = n;
                        p.cy.baseVal.value = t;
                        p.r.baseVal.value = c.dotDia / 2;
                        a.appendChild(p);
                        e && e[l] && (p = document.createElementNS("http://www.w3.org/2000/svg", "tspan"), p.setAttributeNS(null, "x", f(n)), d.appendChild(p), p.setAttributeNS(null, "y", f(t + m / 2 - c.fontBaseline)), p.appendChild(document.createTextNode(e[l])))
                    }
            },
            K = function(a) {
                var d;
                d = (v - 1) * k;
                var h = f(c.nutHeight / 2);
                d = "M" + f(q) + " " + f(r) + " h -" +
                    h + " a" + h + " " + h + " 0 0 1 0 -" + 2 * h + " h" + f(d + 2 * h) + " a" + h + " " + h + " 0 0 1 0 " + 2 * h + " z";
                a.setAttributeNS(null, "d", d)
            },
            L = function(a, d, h, e) {
                d = q + k * d;
                e = r + m * (e - (w ? .5 : b - .5));
                h = f(k * (h - 1));
                var l = c.dotDia / 2,
                    n = f(h / 2 + l / 2),
                    p = c.barHeight,
                    t = p + c.barGirth,
                    g = "M" + f(d - l) + " " + f(e - l),
                    g = g + (" A " + n + " " + f(p) + " 0 0 1 " + f(d + h + l) + " " + f(e - l)),
                    g = g + (" A " + n + " " + f(t) + " 0 0 0 " + f(d - l) + " " + f(e - l));
                a.setAttributeNS(null, "d", g)
            },
            I = function(a, d, h, e) {
                a.setAttributeNS(null, "x", h);
                a.setAttributeNS(null, "y", e);
                a.appendChild(document.createTextNode(d))
            },
            J = function(a, d, h, e) {
                e -= c.fontBaseline;
                for (var b = 0; b < v; b++)
                    if (d[b]) {
                        var n = document.createElementNS("http://www.w3.org/2000/svg", "tspan");
                        n.setAttributeNS(null, "x", f(h + b * k));
                        n.setAttributeNS(null, "y", f(e));
                        n.appendChild(document.createTextNode(d[b]));
                        a.appendChild(n)
                    }
            },
            M = function(a, b) {
                for (var h in b) a.setAttribute(h, b[h])
            },
            f = function(a, b) {
                return Number(a.toFixed(void 0 !== b ? b : 1))
            };
        (function(a, b) {
            for (var h in b) void 0 !== a[h] && (a[h] = b[h])
        })(c, g);
        return function(g, d) {
            (function(a) {
                var e, d, f, g = [],
                    t = [],
                    k = [];
                b = Number.MAX_VALUE;
                u = -b;
                a.head = [];
                v = a.fret.length;
                for (e = 0; e < v; e++) f = a.fret[e], isNaN(f) || 0 > f ? a.head[e] = "x" : 0 == f ? a.head[e] = "o" : (a.head[e] = "", d = t.indexOf(f), 0 > d ? (g.push(e), t.push(f), f < b && (b = f), f > u && (u = f)) : a.label[e] && a.label[e] == a.label[g[d]] ? k[d] = e : g[d] = e);
                b > u && (b = 1, u = c.minSpan);
                x = Math.max(c.minSpan, u - b + 1);
                if (0 < k.length)
                    for (e = 0, z = Number.MAX_VALUE; e < k.length; e++) k[e] && z > t[e] && (z = t[e], D = g[e], y = k[e] - D + 1);
                else y = 0;
                w = !(1 < b && u > x)
            })(d);
            k = c.cellWidth;
            q = c.padding + k / 2 + (w ? 0 : k);
            m = c.cellHeight;
            G = c.padding + m *
                (d.title ? 1 : 0);
            F = G + m;
            r = F + c.nutHeight * (w ? 1 : 0);
            A = f(q + k * (v - .5) + c.padding);
            E = f(r + m * x + (d.footer ? m : 0) + c.padding);
            for (M(g, {
                    "class": "chordChart",
                    xmlns: "http://www.w3.org/2000/svg",
                    width: f(A * (d.scale || 1), 0),
                    height: f(E * (d.scale || 1), 0),
                    viewBox: "0 0 " + f(A, 0) + " " + f(E, 0),
                    preserveAspectRatio: "xMidYMid meet",
                    "font-size": c.fontHeight
                }); 0 < g.childNodes.length;) g.removeChild(g.lastChild);
            (function(b) {
                for (var e in b)
                    for (var f = e, c = b[e].split(","), g = d.style, k = 0; k < c.length; k++) a[c[k]] = document.createElementNS("http://www.w3.org/2000/svg",
                        f), a[c[k]].className.baseVal = c[k], g && g[c[k]] && a[c[k]].setAttributeNS(null, "style", g[c[k]])
            })({
                g: "grid,dots,text",
                path: "frets,strings,nut,barre",
                text: "title,header,labels,lofret,footer"
            });
            d.style && d.style.root && g.setAttributeNS(null, "style", d.style.root);
            g.appendChild(a.grid);
            g.appendChild(a.dots);
            H(a.dots, a.labels, d.fret, d.label);
            g.appendChild(a.text);
            a.text.setAttributeNS(null, "text-anchor", "middle");
            a.grid.appendChild(a.frets);
            B(a.frets);
            a.grid.appendChild(a.strings);
            C(a.strings);
            a.text.appendChild(a.header);
            J(a.header, d.head, q, F);
            w ? (g.appendChild(a.nut), K(a.nut)) : (a.text.appendChild(a.lofret), I(a.lofret, b, c.padding + k / 2, r + m - c.fontBaseline));
            (void 0 == d.barre || d.barre) && 1 < y && 0 < b && (g.appendChild(a.barre), L(a.barre, D, y, z));
            d.footer && (a.text.appendChild(a.footer), J(a.footer, d.footer, q, r + m * (x + 1)));
            d.label && a.text.appendChild(a.labels);
            d.title && (a.text.appendChild(a.title), I(a.title, d.title, f(A / 2), f(G)))
        }
    }(function(g, a) {
        if (!g && !a) return {};
        g = g || 16;
        a = a || 1.2;
        var c = function(a) {
                return Number(a.toFixed(1))
            },
            b = {
                fontHeight: g,
                dotDia: c(1.2 * g)
            };
        1 > a ? (b.cellHeight = c(1.2 * b.dotDia), b.padding = c(.2 * b.cellHeight), b.cellWidth = c(b.cellHeight / a)) : (b.cellWidth = c(1.2 * b.dotDia), b.padding = c(.2 * b.cellWidth), b.cellHeight = c(b.cellWidth * a));
        b.fontBaseline = c((b.cellHeight - .7 * b.fontHeight) / 2);
        b.nutHeight = c(.2 * b.cellHeight);
        b.barHeight = c(.35 * b.cellHeight);
        b.barGirth = c(.1 * b.cellHeight);
        return b
    }(B, C));
    return function(g, a) {
        var c = {},
            b;
        for (b in a) c[b] = a[b];
        if (a.fret)
            for (c.fret = a.fret.split(","), b = 0; b < c.fret.length; b++) c.fret[b] = parseInt(c.fret[b],
                10);
        a.label && (c.label = a.label.split(","));
        a.footer && (c.footer = a.footer.split(","));
        H(g, c)
    }
};
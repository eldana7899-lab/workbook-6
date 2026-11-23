"""Generates the Workbook 6a asset-portfolio UML class diagram (SVG + printable HTML).

Run:  python3 build_diagram.py
Writes ../asset-portfolio-uml.svg and ./diagram.html (used to export PDF/PNG).
"""
from html import escape
import pathlib

LINE, PAD = 20, 8
CW = 7.6          # approx px per character at 14px Helvetica
INK = "#1f2a37"
out = []
boxes = {}


# ---------------------------------------------------------------- classes
class Cls:
    def __init__(self, name, attrs, methods, stereo=None, italic=False, head="#dbe7f5"):
        self.name, self.attrs, self.methods = name, attrs, methods
        self.stereo, self.italic, self.head = stereo, italic, head
        self.w = max(len(s) for s in attrs + methods + [name]) * CW + 30
        self.hdr = 40 + (14 if stereo else 0)
        self.a_h = (len(attrs) * LINE + PAD * 2) if attrs else PAD * 2
        self.m_h = len(methods) * LINE + PAD * 2
        self.h = self.hdr + self.a_h + self.m_h


def draw(key, c, x, y):
    boxes[key] = (x, y, c.w, c.h)
    out.append(f'<rect x="{x}" y="{y}" width="{c.w}" height="{c.h}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
    out.append(f'<rect x="{x}" y="{y}" width="{c.w}" height="{c.hdr}" fill="{c.head}" stroke="{INK}" stroke-width="1.6"/>')
    cx, ty = x + c.w / 2, y + 26
    if c.stereo:
        out.append(f'<text x="{cx}" y="{y + 19}" text-anchor="middle" font-size="12">{escape(c.stereo)}</text>')
        ty += 14
    it = ' font-style="italic"' if c.italic else ''
    out.append(f'<text x="{cx}" y="{ty}" text-anchor="middle" font-weight="bold" font-size="16"{it}>{escape(c.name)}</text>')
    yy = y + c.hdr
    for i, s in enumerate(c.attrs):
        out.append(f'<text x="{x + 12}" y="{yy + PAD + 15 + i * LINE}">{escape(s)}</text>')
    yy += c.a_h
    out.append(f'<line x1="{x}" y1="{yy}" x2="{x + c.w}" y2="{yy}" stroke="{INK}" stroke-width="1.2"/>')
    for i, s in enumerate(c.methods):
        it = ' font-style="italic"' if "{abstract}" in s else ''
        out.append(f'<text x="{x + 12}" y="{yy + PAD + 15 + i * LINE}"{it}>{escape(s)}</text>')


def cx(k): x, y, w, h = boxes[k]; return x + w / 2
def top(k): return boxes[k][1]
def bot(k): x, y, w, h = boxes[k]; return y + h


def poly(pts, dashed=False):
    d = " ".join(f"{a},{b}" for a, b in pts)
    da = ' stroke-dasharray="8,6"' if dashed else ''
    out.append(f'<polyline points="{d}" fill="none" stroke="{INK}" stroke-width="1.6"{da}/>')


def tri_up(px, py):
    """Hollow triangle with its tip at (px, py) - UML generalization/realization head."""
    out.append(f'<polygon points="{px},{py} {px - 11},{py + 17} {px + 11},{py + 17}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
    return py + 17


def label(x, y, s, anchor="middle", size=13, weight="normal", fill=INK):
    out.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-size="{size}" font-weight="{weight}" fill="{fill}">{escape(s)}</text>')


def note(x, y, w, lines, to=None):
    h = len(lines) * 18 + 16
    out.append(f'<path d="M{x},{y} H{x + w - 14} L{x + w},{y + 14} V{y + h} H{x} Z" fill="#fff8d6" stroke="#8a6d00" stroke-width="1.2"/>')
    out.append(f'<path d="M{x + w - 14},{y} V{y + 14} H{x + w}" fill="none" stroke="#8a6d00" stroke-width="1.2"/>')
    for i, s in enumerate(lines):
        out.append(f'<text x="{x + 10}" y="{y + 21 + i * 18}" font-size="13" xml:space="preserve">{escape(s)}</text>')
    if to:
        (sx, sy), (ex, ey) = to
        out.append(f'<line x1="{sx}" y1="{sy}" x2="{ex}" y2="{ey}" stroke="#8a6d00" stroke-width="1.2" stroke-dasharray="4,4"/>')
    return h


# ---------------------------------------------------------------- model
valuable = Cls("Valuable", [], ["+ getValue(): double"], stereo="«interface»", italic=True, head="#e6dcf7")

portfolio = Cls("Portfolio",
                ["- name: String", "- owner: String", "- assets: ArrayList<Valuable>"],
                ["+ Portfolio(name: String, owner: String)",
                 "+ add(item: Valuable): void",
                 "+ getValue(): double",
                 "+ getMostValuable(): Valuable",
                 "+ getLeastValuable(): Valuable"], head="#fde2cf")

asset = Cls("Asset", ["- name: String", "- marketValue: double"],
            ["+ Asset(name: String, marketValue: double)",
             "+ getName(): String",
             "+ getMarketValue(): double",
             "+ getValue(): double {abstract}"],
            stereo="«abstract»", italic=True)

bank = Cls("BankAccount", ["- name: String", "- accountNumber: String", "- balance: double"],
           ["+ BankAccount(name, accountNumber, balance)",
            "+ deposit(amount: double): void",
            "+ withdraw(amount: double): void",
            "+ getName(): String",
            "+ getBalance(): double",
            "+ getValue(): double"], head="#d8f0e0")

card = Cls("CreditCard", ["- name: String", "- accountNumber: String", "- balance: double"],
           ["+ CreditCard(name, accountNumber, balance)",
            "+ charge(amount: double): void",
            "+ pay(amount: double): void",
            "+ getName(): String",
            "+ getBalance(): double",
            "+ getValue(): double"], head="#f7d9dc")

house = Cls("House", ["- yearBuilt: int", "- squareFeet: int", "- bedrooms: int"],
            ["+ House(name, marketValue, yearBuilt, squareFeet, bedrooms)", "+ getValue(): double"])

jewelry = Cls("Jewelry", ["- karat: double"],
              ["+ Jewelry(name, marketValue, karat)", "+ getValue(): double"])

# ---------------------------------------------------------------- layout
ROW2 = 380
GAP = 70
SUB_GAP = 40
HX = 30
subs_right = HX + house.w + SUB_GAP + jewelry.w

row_w = asset.w + bank.w + card.w + 2 * GAP
# push the account classes right so the fixed-asset subclasses never sit under them
x0 = max(140, subs_right + 50 - asset.w - GAP)
W = int(x0 + row_w + 40)
draw("asset", asset, x0, ROW2)
draw("bank", bank, x0 + asset.w + GAP, ROW2)
draw("card", card, x0 + asset.w + bank.w + 2 * GAP, ROW2)

draw("valuable", valuable, cx("bank") - valuable.w / 2, 110)
draw("portfolio", portfolio, 40, 80)

# realization: Asset, BankAccount, CreditCard ..|> Valuable  (shared dashed bus)
VX = cx("valuable")
base = tri_up(VX, bot("valuable"))
BUS = ROW2 - 55
poly([(VX, base), (VX, BUS)], dashed=True)
poly([(cx("asset"), BUS), (cx("card"), BUS)], dashed=True)
for k in ("asset", "bank", "card"):
    poly([(cx(k), BUS), (cx(k), top(k))], dashed=True)
label(VX + 12, BUS - 10, "implements", anchor="start", size=12, fill="#555")

# aggregation: Portfolio <>---- 0..* Valuable
py = boxes["valuable"][1] + valuable.h / 2
px = boxes["portfolio"][0] + portfolio.w
vx_left = boxes["valuable"][0]
out.append(f'<polygon points="{px},{py} {px + 13},{py - 8} {px + 26},{py} {px + 13},{py + 8}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
poly([(px + 26, py), (vx_left, py)])
label(px + 34, py - 8, "1", anchor="start")
label(vx_left - 8, py - 8, "0..*", anchor="end")
label((px + vx_left) / 2 + 13, py + 22, "assets", size=12, fill="#555")

# third row: House, Jewelry under Asset  (generalization, solid)
ROW3 = bot("card") + 110
NOTE_Y = bot("card") + 45
draw("house", house, HX, ROW3)
draw("jewelry", jewelry, HX + house.w + SUB_GAP, ROW3)
AX = cx("asset")
base = tri_up(AX, bot("asset"))
BUS3 = ROW3 - 40
poly([(AX, base), (AX, BUS3)])
poly([(cx("house"), BUS3), (cx("jewelry"), BUS3)])
for k in ("house", "jewelry"):
    poly([(cx(k), BUS3), (cx(k), top(k))])
label(AX + 10, BUS3 - 10, "extends", anchor="start", size=12, fill="#555")

# ---------------------------------------------------------------- notes
cbx, cby, cbw, cbh = boxes["card"]
nw = cbw + 30
nx = cbx + cbw - nw
nh = note(nx, NOTE_Y, nw, [
    "CreditCard.getValue() returns -balance",
    "(balance = amount owed). Debt counts as a",
    "negative value, so it lowers net worth.",
    "charge(amt):  balance += amt",
    "pay(amt):     balance -= amt",
], to=((nx + nw / 2, NOTE_Y), (cx("card"), bot("card"))))

bbx, bby, bbw, bbh = boxes["bank"]
note(bbx, NOTE_Y, bbw, [
    "BankAccount.getValue() returns balance.",
    "deposit(amt):   balance += amt",
    "withdraw(amt):  balance -= amt",
], to=((bbx + bbw / 2, NOTE_Y), (cx("bank"), bot("bank"))))

ppx, ppy, ppw, pph = boxes["portfolio"]
pnw = ppw
pny = ppy + pph + 40
note(ppx, pny, pnw, [
    "getValue(): adds up item.getValue() for",
    "every Valuable in assets. Portfolio never",
    "checks whether an item is a House, Bank-",
    "Account, Jewelry or CreditCard;",
    "it only relies on the Valuable interface.",
], to=((ppx + pnw / 2, pny), (ppx + ppw / 2, ppy + pph)))

# title + legend
H = int(max(bot("house"), bot("jewelry"), NOTE_Y + nh) + 150)
label(W / 2, 40, "Net Worth Portfolio: Updated Class Diagram", size=24, weight="bold")
label(W / 2, 64, "Workbook 6a · Exercise: Expanding the Asset Portfolio", size=14, fill="#555")

LY = H - 100
lx = W - 470
out.append(f'<rect x="{lx - 16}" y="{LY - 26}" width="440" height="116" fill="#f7f8fa" stroke="#c8ccd2"/>')
label(lx, LY - 6, "Legend", anchor="start", size=13, weight="bold")
poly([(lx, LY + 18), (lx + 60, LY + 18)], dashed=True)
out.append(f'<polygon points="{lx + 76},{LY + 18} {lx + 60},{LY + 8} {lx + 60},{LY + 28}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
label(lx + 92, LY + 23, "realization (class implements interface)", anchor="start")
poly([(lx, LY + 46), (lx + 60, LY + 46)])
out.append(f'<polygon points="{lx + 76},{LY + 46} {lx + 60},{LY + 36} {lx + 60},{LY + 56}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
label(lx + 92, LY + 51, "generalization (subclass extends class)", anchor="start")
out.append(f'<polygon points="{lx},{LY + 74} {lx + 13},{LY + 66} {lx + 26},{LY + 74} {lx + 13},{LY + 82}" fill="#fff" stroke="{INK}" stroke-width="1.6"/>')
poly([(lx + 26, LY + 74), (lx + 76, LY + 74)])
label(lx + 92, LY + 79, "aggregation (Portfolio holds Valuables)", anchor="start")

for i, t in enumerate(["-  private member", "+  public member", "italic name  =  abstract class / interface",
                       "{abstract}  =  abstract method"]):
    label(lx - 380, LY - 6 + i * 22, t, anchor="start", size=12, fill="#555")

svg = (f'<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}" '
       f'font-family="Helvetica, Arial, sans-serif" font-size="14" fill="{INK}">'
       f'<rect width="{W}" height="{H}" fill="#fff"/>' + "".join(out) + "</svg>")

here = pathlib.Path(__file__).parent
(here.parent / "asset-portfolio-uml.svg").write_text(svg, encoding="utf-8")
(here / "diagram.html").write_text(
    f'<!doctype html><html><head><meta charset="utf-8"><style>'
    f'@page{{size:{W}px {H}px;margin:0}}html,body{{margin:0;padding:0;background:#fff}}'
    f'svg{{display:block}}</style></head><body>{svg}</body></html>', encoding="utf-8")
print(W, int(H))

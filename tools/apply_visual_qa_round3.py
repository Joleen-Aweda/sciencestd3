import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def update(name: str, transform) -> None:
    path = ROOT / name
    path.write_text(transform(path.read_text(encoding="utf-8")), encoding="utf-8")


def page27(text: str) -> str:
    text = text.replace(
        'text-[1.05rem] leading-snug',
        'text-[1.35rem] leading-[1.5]',
    ).replace(
        'max-lg:text-[1rem] max-sm:text-[0.92rem]',
        'max-lg:text-[1.2rem] max-sm:text-[1rem]',
    )
    grid = '''<div class="grid grid-cols-3 items-start gap-x-8 gap-y-8 max-lg:gap-x-6 max-sm:grid-cols-1 max-sm:gap-y-8">
        <div class="flex flex-col items-center"><div data-id="pg027_n0022" class="mb-2 text-[1.35rem] font-semibold">(a)</div><img src="images/shape_pg027_im004_crop_v1.png" alt="Blue square." data-id="pg027_im004_crop_v1" class="h-[150px] w-[190px] object-contain max-sm:h-auto"></div>
        <div class="flex flex-col items-center"><div data-id="pg027_n0024" class="mb-2 text-[1.35rem] font-semibold">(b)</div><img src="images/shape_pg027_im003.png" alt="Red triangle." data-id="pg027_im003" class="h-[156px] w-[211px] object-contain max-sm:h-auto"></div>
        <div class="flex flex-col items-center"><div data-id="pg027_n0026" class="mb-2 text-[1.35rem] font-semibold">(c)</div><img src="images/shape_pg027_im002.png" alt="Green circle." data-id="pg027_im002" class="h-[186px] w-[186px] object-contain max-sm:h-auto"></div>
        <div class="flex flex-col items-center"><div data-id="pg027_n0028" class="mb-2 text-[1.35rem] font-semibold">(d)</div><img src="images/shape_pg027_im005_crop_v1.png" alt="Yellow cylinder." data-id="pg027_im005_crop_v1" class="h-[232px] w-[139px] object-contain max-sm:h-auto"></div>
        <div class="col-span-2 flex flex-col items-center max-sm:col-span-1"><div data-id="pg027_n0030" class="mb-2 text-[1.35rem] font-semibold">(e)</div><img src="images/shape_pg027_im006.png" alt="Black rectangle." data-id="pg027_im006" class="h-[156px] w-[345px] object-contain max-sm:h-auto"></div>
      </div>'''
    grid = grid.replace('class="mb-2 text-[1.35rem] font-semibold"', 'class="adt-label-above mb-2 text-[1.35rem] font-semibold"')
    text, count = re.subn(
        r'<div class="grid grid-cols-3.*?</div></div><div class="mt-5 text-center">',
        grid + '<div class="mt-5 text-center">',
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("Could not rebuild page 27 shape grid")
    return text


def page46(text: str) -> str:
    text = text.replace('text-[2rem] font-bold', 'text-[2.4rem] font-bold')
    text = text.replace('text-[1rem] leading-[1.55]', 'text-[1.35rem] leading-[1.55]')
    figure = '''<figure class="mx-auto mb-2 max-w-5xl">
        <div class="sr-only"><span data-id="pg046_n0018">Light ↓</span> <span data-id="pg046_n0020">← Light</span> <span data-id="pg046_n0022">Light →</span></div>
        <img data-id="pg046_im001" src="images/pg046_figure3_reference.png" alt="Three potted plants respond to light: one grows upright under light from above, one bends left toward light entering from the left, and one bends right toward light entering from the right." class="h-auto w-full object-contain">
        <figcaption data-id="pg046_n0023" class="mt-3 text-center text-[1.05rem] italic text-zinc-800 max-sm:text-[0.95rem]">Figure 3: Plants responding to light stimulus</figcaption>
      </figure>'''
    text, count = re.subn(
        r'<div class="mb-2 flex items-end.*?<div data-id="pg046_n0023".*?</div>',
        figure,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("Could not replace page 46 diagram")
    return text


def page48(text: str) -> str:
    text = text.replace('text-3xl', 'text-[1.35rem]')
    text = text.replace('max-lg:text-2xl', 'max-lg:text-[1.2rem]')
    text = text.replace('max-sm:text-xl', 'max-sm:text-[1rem]')
    text = text.replace('text-4xl font-extrabold', 'text-[2.4rem] font-extrabold')
    figure = '''<figure class="mx-auto mb-4 max-w-5xl">
      <div class="sr-only"><span data-id="pg048_n0021">Light ↓</span> <span data-id="pg048_n0022">Plant A under light</span> <span data-id="pg048_n0024">Light →</span> <span data-id="pg048_n0025">Plant B in the box</span></div>
      <img src="images/pg048_figure6_reference.png" data-id="pg048_im002" alt="Plant A stands under light from above. Plant B is inside a box and bends toward light entering through a round side hole." class="h-auto w-full object-contain">
      <figcaption data-id="pg048_n0026" class="mt-3 text-center text-[1.05rem] italic text-gray-700 max-sm:text-[0.95rem]">Figure 6: Investigating how a plant moves towards light</figcaption>
    </figure>'''
    text, count = re.subn(
        r'<div class="mb-4 grid grid-cols-2.*?<div data-id="pg048_n0026".*?</div>',
        figure,
        text,
        count=1,
        flags=re.DOTALL,
    )
    if count != 1:
        raise RuntimeError("Could not replace page 48 diagram")
    return text


def page61(text: str) -> str:
    text = text.replace('flex flex-col gap-8 container', 'flex flex-col gap-3 container')
    text = text.replace(' bg-white min-h-[980px] max-lg:min-h-[860px] max-sm:min-h-0', ' bg-white')
    text = text.replace('text-[3.2rem]', 'text-[2.4rem]')
    text = re.sub(
        r'\s*<div class="relative z-10 mt-auto flex items-end justify-between.*?</div>\s*</section>',
        '\n  </section>',
        text,
        count=1,
        flags=re.DOTALL,
    )
    text = text.replace(' bg-white min-h-screen border-l-', ' bg-white border-l-')
    text = text.replace('text-[32px]', 'text-[2rem]')
    text = text.replace('text-[24px]', 'text-[1.35rem]')
    return text


update("pg027_sec002.html", page27)
update("pg046_sec001.html", page46)
update("pg048_sec001.html", page48)
update("pg061_sec003.html", page61)

texts_path = ROOT / "content/i18n/en/texts.json"
texts = json.loads(texts_path.read_text(encoding="utf-8"))
texts.update({
    "pg027_n0022": "(a)",
    "pg027_n0024": "(b)",
    "pg027_n0026": "(c)",
    "pg027_n0028": "(d)",
    "pg027_n0030": "(e)",
    "pg046_im001": "Three potted plants respond to light: one grows upright under light from above, one bends left toward light entering from the left, and one bends right toward light entering from the right.",
    "pg048_im002": "Plant A stands under light from above. Plant B is inside a box and bends toward light entering through a round side hole.",
})
texts_path.write_text(json.dumps(texts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print("Applied page 27, 46, 48 and 61 visual QA corrections.")

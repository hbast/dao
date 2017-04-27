# DAO - DocBook Accessibility Optimizer for Apache FOP

DAO is a script written in Python that optimizes the \<fo:block\> structures of XSL-FO code generated by DocBook-XSL. The optimized XSL-FO code can then be used with FOP for generating tagged PDF. The tag structure of the resulting PDF will be as flat as possible.

## Introduction
Apache FOP can be used to generate tagged PDF from XSL-FO code. Using DocBook XML in conjunction with the official DocBook-XSL files leads to the problem that deep nested \<fo:block\> structures are generated. Because FOP automatically tags every \<fo:block\> as paragraph (PDF tag 'P'), the resulting PDF tag structure looks pretty 'weak'.

DAO solves that problem by crwaling through the XSL-FO document structure and optimizing the \<fo:block\> structure.

```
+---------+        +--------+        +--------+        +-----+
| DocBook |  XSL   | XSL-FO |  DAO   | XSL-FO |  FOP   | PDF |
|   XML   +------->|        +------->|  opt   +------->|     |
+---------+        +--------+        +--------+        +-----+
```

## Usage



## Example

XSL-FO before optimization:
```xml
<fo:block id="d0e9">
  <fo:block font-family="sans-serif,Symbol,ZapfDingbats">
    <fo:block start-indent="0pt" text-align="center">
      <fo:block keep-with-next.within-column="always" font-size="24.8832pt" font-weight="bold">
        <fo:block keep-with-next.within-column="always" space-before.optimum="10pt"
        space-before.minimum="10pt * 0.8" space-before.maximum="10pt * 1.2" hyphenate="false"
        text-align="start" start-indent="0pt" hyphenation-character="-"
        hyphenation-push-character-count="2"
        hyphenation-remain-character-count="2">Test Document</fo:block>
      </fo:block>
    </fo:block>
  </fo:block>
</fo:block>
```

XSL-FO after DAO-optimization:
```xml
<fo:block keep-with-next.within-column="always" space-before.optimum="10pt"
space-before.minimum="10pt * 0.8" space-before.maximum="10pt * 1.2" hyphenate="false"
text-align="start" start-indent="0pt" hyphenation-character="-" hyphenation-push-character-count="2"
hyphenation-remain-character-count="2" font-size="24.8832pt"
font-family="sans-serif,Symbol,ZapfDingbats" id="d0e9" font-weight="bold">Test Document</fo:block>
```

PDF tag structure before optimization:
```xml
<p>
  <p>
    <p>
      <p>
        <p>Test Document</p>
      </p>
    </p>
  </p>
</p>
```

PDF tag structure after DAO-optimization:
```xml
<p>Test Document</p>
```

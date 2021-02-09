def _international(n, d) -> str:
    return d.get(n + "colour") or d.get(n + "color") or ""


class ColourOptions(dict):
    SMALL_ONLY = ["avatar_background", "leftcolour", "rightcolour", "lefttext", "righttext"]
    LARGE_ONLY = [
        "topcolour",
        "midcolour",
        "usernamecolour",
        "certifiedcolour",
        "datacolour",
        "labelcolour",
        "highlightcolour",
    ]

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # large widget
        self.topcolour = (_international("top", kwargs) or _international("top_", kwargs)).lstrip("#")
        self.midcolour = (_international("mid", kwargs) or _international("mid_", kwargs)).lstrip("#")
        self.usernamecolour = (_international("username", kwargs) or _international("username_", kwargs)).lstrip("#")
        self.certifiedcolour = (_international("certified", kwargs) or _international("certified_", kwargs)).lstrip("#")
        self.datacolour = (_international("data", kwargs) or _international("data_", kwargs)).lstrip("#")
        self.labelcolour = (_international("label", kwargs) or _international("label_", kwargs)).lstrip("#")
        self.highlightcolour = (_international("highlight", kwargs) or _international("highlight_", kwargs)).lstrip("#")

        # smol widget
        self.avatar_background = (
            _international("avatar_background", kwargs) or _international("avatar_", kwargs)
        ).lstrip("#")
        self.leftcolour = (_international("left", kwargs) or _international("left_", kwargs)).lstrip("#")
        self.rightcolour = (_international("right", kwargs) or _international("right_", kwargs)).lstrip("#")
        self.lefttext = (_international("left_text", kwargs) or _international("left_text_", kwargs)).lstrip("#")
        self.righttext = (_international("right_text", kwargs) or _international("right_text_", kwargs)).lstrip("#")
        self._validate()

    def _validate(self):
        for key, value in self.__dict__.items():
            if value:
                try:
                    n = int(value, base=16)
                    if n > 16777215:
                        raise ValueError
                except ValueError:
                    raise ValueError(f"'#{value}' is not a valid hexadecimal.")
        return True

    def __repr__(self):
        t = "{}='{}'"
        values = []
        for attr, value in self.__dict__.items():
            values.append(t.format(attr, str(value)))
        return "ColourOptions({})".format(", ".join(values))

    def to_uri(self, widget_type: str):
        if not bool(self):
            return ""
        result = []
        if widget_type.lower() == "large":
            for attrname in self.LARGE_ONLY:
                col = getattr(self, attrname)
                if col:
                    result.append(attrname + "=" + col[:6])
        else:
            for attrname in self.SMALL_ONLY:
                col = getattr(self, attrname)
                if col:
                    result.append(attrname + "=" + col[:6])
        return "&".join(result)

    def __bool__(self):
        return any(bool(x) for x in self.__dict__.values())

    def usable(self, key):
        if key == "small":
            return any(bool(getattr(self, x)) for x in self.SMALL_ONLY)
        return any(bool(getattr(self, x)) for x in self.LARGE_ONLY)


# noinspection PyShadowingBuiltins
def large_widget(id: int, format: str = "svg", *, formatting: ColourOptions = None) -> str:
    """Generates a URL for the large widget of the provided ID."""
    if formatting is None:
        formatting = ColourOptions()
    if format.lower() not in ["png", "svg"]:
        raise TypeError("Widget format must be PNG or SVG.")

    url = "https://top.gg/api/widget/{}.{}".format(str(id), format)
    if formatting.usable("large"):
        url += "?" + formatting.to_uri("large").replace("colour", "color")
    return url


def small_widget(id: int, format: str = "svg", *, formatting: ColourOptions = None, key: str):
    if formatting is None:
        formatting = ColourOptions()
    valid_keys = ["owner", "status", "upvotes", "servers", "lib"]
    key = key.lower()
    if key not in valid_keys:
        raise TypeError("Widget key must be one of: " + ", ".join(valid_keys))

    if format.lower() not in ["png", "svg"]:
        raise TypeError("Widget format must be PNG or SVG.")

    url = "https://top.gg/api/widget/{}/{}.{}".format(key, str(id), format)
    if formatting.usable("small"):
        url += "?" + formatting.to_uri("small").replace("colour", "color")
    return url

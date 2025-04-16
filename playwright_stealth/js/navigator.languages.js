const languages = opts.navigator.languages.length ? opts.navigator.languages : ["en-US", "en"];
const primaryLanguage = languages[0];

utils.replaceGetterWithProxy(
    Object.getPrototypeOf(navigator),
    "languages",
    utils.makeHandler().getterValue(Object.freeze([...languages]))
);

utils.replaceGetterWithProxy(
    Object.getPrototypeOf(navigator),
    "language",
    utils.makeHandler().getterValue(primaryLanguage)
);
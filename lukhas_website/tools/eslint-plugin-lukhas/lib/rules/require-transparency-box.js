"use strict";

/**
 * Warn if a Next.js page under /app/(public|auth)/**/page.(tsx|jsx)
 * does not render a <TransparencyBox .../> somewhere in the file.
 * This is a *warning* (not blocking). CI can elevate if desired.
 */
module.exports = {
  meta: {
    type: "suggestion",
    docs: { description: "Require TransparencyBox on public/auth pages" },
    messages: {
      missing: "Public/auth page should include <TransparencyBox /> for capabilities/limits."
    },
    schema: []
  },
  create(context) {
    const filename = context.getFilename().replace(/\\/g, "/");
    const isTarget =
      /\/app\/\((public|auth)\)\/.*\/page\.(tsx|jsx)$/.test(filename);

    if (!isTarget) return {};

    let hasTransparency = false;

    return {
      JSXOpeningElement(node) {
        if (node.name && node.name.name === "TransparencyBox") {
          hasTransparency = true;
        }
      },
      'Program:exit'() {
        if (!hasTransparency) {
          context.report({ loc: { line: 1, column: 0 }, messageId: "missing" });
        }
      }
    };
  }
};

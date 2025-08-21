import React from "react";
import TransparencyBox from "@/components/TransparencyBox";

export function withTransparencyBox<P extends Record<string, any>>(
  Page: React.ComponentType<P>
) {
  return function Wrapped(props: P) {
    return (
      <>
        <TransparencyBox
          capabilities={["Passkeys (WebAuthn)", "Magic links (time-limited)"]}
          limitations={["Device support varies", "Email delivery can be delayed"]}
          dependencies={["System authenticator", "Email provider", "Identity service"]}
          dataHandling="No biometrics leave your device. We store public keys only."
        />
        <Page {...props} />
      </>
    );
  };
}
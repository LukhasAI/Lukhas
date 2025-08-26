import React from "react";
import TransparencyBox from "@/components/TransparencyBox";

type TBProps = React.ComponentProps<typeof TransparencyBox>;

const defaultProps: TBProps = {
  capabilities: ["Passkeys (WebAuthn)", "Magic links (time-limited)"],
  limitations: ["Device support varies", "Email delivery can be delayed"],
  dependencies: ["System authenticator", "Email provider", "Identity service"],
  dataHandling: "No biometrics leave your device. We store public keys only."
};

export function withTransparencyBox<P>(Page: React.ComponentType<P>, tbProps?: Partial<TBProps>) {
  return function Wrapped(props: P) {
    return (
      <>
        <TransparencyBox {...defaultProps} {...tbProps} />
        <Page {...props} />
      </>
    );
  };
}

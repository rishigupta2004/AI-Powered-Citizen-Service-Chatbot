import React, { useEffect, useState } from "react";
import { createFeatureFlag } from "../flags";

const FeatureFlagDemo: React.FC = () => {
  const [enabled, setEnabled] = useState<boolean | null>(null);

  useEffect(() => {
    createFeatureFlag("my_feature_flag")().then(setEnabled);
  }, []);

  return (
    <div>
      myFeatureFlag is {enabled === null ? "loading..." : enabled ? "on" : "off"}
    </div>
  );
};

export default FeatureFlagDemo;

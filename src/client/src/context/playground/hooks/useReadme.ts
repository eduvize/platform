import { useContextSelector } from "use-context-selector";
import { PlaygroundContext } from "../PlaygroundContext";
import { ReactNode } from "react";

export const useReadme = (): ReactNode | string | undefined => {
    const readme = useContextSelector(PlaygroundContext, (x) => x.readme);

    return readme;
};

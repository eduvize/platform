import { PlaygroundProvider } from "@context/playground";
import { Playground } from "@organisms";

export const PlaygroundTest = () => {
    return (
        <PlaygroundProvider>
            <Playground />
        </PlaygroundProvider>
    );
};

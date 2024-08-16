import { useContext } from "use-context-selector";
import { AuthContext } from "@context/auth";
import { OAuthProvider } from "@models/enums";

interface OAuthProviderReturn {
    redirect: (provider: OAuthProvider) => void;
    exchange: (code: string) => void;
}

export const useOAuth = (): OAuthProviderReturn => {
    const { oauthExchange, oauthRedirect } = useContext(AuthContext);

    return {
        redirect: oauthRedirect,
        exchange: oauthExchange,
    };
};

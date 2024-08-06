import { UseFormReturnType } from "@mantine/form";
import { ProfileUpdatePayload } from "../../../api/contracts";
import { SearchInput, SpacedDivider } from "../../../components/molecules";
import AutocompleteApi from "../../../api/AutocompleteApi";
import { Stack } from "@mantine/core";

interface EducationStepProps {
    form: UseFormReturnType<ProfileUpdatePayload>;
}

export const EducationStep = ({ form }: EducationStepProps) => {
    return (
        <>
            <SpacedDivider
                bold
                label="Where did you study?"
                labelPosition="left"
                labelColor="blue"
                labelSize="lg"
                spacePlacement="bottom"
                spacing="lg"
            />

            <Stack>
                <SearchInput
                    valueFetch={(query) =>
                        AutocompleteApi.getEducationalInstitutions(query)
                    }
                    label="Institution"
                    placeholder="University, college, bootcamp, etc."
                />

                <SearchInput
                    valueFetch={(query) =>
                        AutocompleteApi.getEducationalInstitutions(query)
                    }
                    label="Area of Study"
                    placeholder="Major, minor, concentration, etc."
                />
            </Stack>
        </>
    );
};

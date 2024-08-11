import { ProfileStep } from "./constants";
import {
    isBasicInformationComplete,
    isEducationInformationComplete,
    isHobbyInformationComplete,
    isProfessionalInformationComplete,
} from "./validation";
import { Image, Stepper } from "@mantine/core";
import { UseFormReturnType } from "@mantine/form";
import {
    IconUser,
    IconHammer,
    IconBellSchool,
    IconDeviceLaptop,
    IconStar,
} from "@tabler/icons-react";
import { useEffect, useMemo } from "react";
import { ProfileUpdatePayload } from "../../api/contracts";
import { LearningCapacity } from "../../models/enums";
import { UserDto } from "../../models/dto/user/UserDto";

interface ProfileStepperProps {
    userDetails: UserDto | null;
    pendingSave: boolean;
    form: UseFormReturnType<ProfileUpdatePayload>;
    currentStep: ProfileStep;
    disabled?: boolean;
    onChangeStep: (step: ProfileStep) => void;
}

export const ProfileStepper = ({
    userDetails,
    pendingSave,
    form,
    disabled,
    currentStep,
    onChangeStep,
}: ProfileStepperProps) => {
    const visibleSteps = useMemo(() => {
        let steps = form.values.learning_capacities.reduce(
            (acc, capacity) => {
                switch (capacity) {
                    case LearningCapacity.Hobby:
                        return acc.concat("hobby");
                    case LearningCapacity.Student:
                        return acc.concat("education");
                    case LearningCapacity.Professional:
                        return acc.concat("professional");
                    default:
                        return acc;
                }
            },
            ["basic"]
        ) as any[];

        if (form.values.skills.length > 0) {
            steps = steps.concat("proficiencies");
        }

        return steps;
    }, [form.values.learning_capacities, form.values.skills]);

    const stepIndex = useMemo(
        () => visibleSteps.indexOf(currentStep),
        [currentStep, visibleSteps]
    );

    useEffect(() => {
        onChangeStep(visibleSteps[stepIndex]);
    }, [stepIndex, visibleSteps]);

    const canSelectHobby = useMemo(
        () => isBasicInformationComplete(form),
        [form.values]
    );
    const canSelectEducation = useMemo(
        () =>
            isBasicInformationComplete(form) &&
            isHobbyInformationComplete(form),
        [form.values]
    );
    const canSelectProfessional = useMemo(
        () =>
            isBasicInformationComplete(form) &&
            isHobbyInformationComplete(form) &&
            isEducationInformationComplete(form),
        [form.values]
    );
    const canSelectProficiencies = useMemo(
        () =>
            isBasicInformationComplete(form) &&
            isHobbyInformationComplete(form) &&
            isEducationInformationComplete(form) &&
            isProfessionalInformationComplete(form),
        [form.values]
    );

    const getStepTextColor = (step: ProfileStep) => {
        return currentStep === step
            ? "var(--mantine-color-gray-1)"
            : (() => {
                  switch (step) {
                      case "hobby":
                          return !canSelectHobby
                              ? "var(--mantine-color-gray-7)"
                              : undefined;
                      case "education":
                          return !canSelectEducation
                              ? "var(--mantine-color-gray-7)"
                              : undefined;
                      case "professional":
                          return !canSelectProfessional
                              ? "var(--mantine-color-gray-7)"
                              : undefined;
                      case "proficiencies":
                          return !canSelectProficiencies
                              ? "var(--mantine-color-gray-7)"
                              : undefined;
                      default:
                          return undefined;
                  }
              })();
    };

    const getStepProps = (step: ProfileStep) => ({
        styles: {
            stepLabel: {
                color: getStepTextColor(step),
            },
            stepDescription: {
                color: getStepTextColor(step),
            },
        },
        loading: currentStep === step && pendingSave,
        disabled: disabled,
    });

    return (
        <Stepper
            active={stepIndex}
            orientation="vertical"
            onStepClick={(index) => onChangeStep(visibleSteps[index])}
        >
            <Stepper.Step
                {...getStepProps("basic")}
                key="basic"
                label="General Information"
                description="The basics about you"
                completedIcon={
                    userDetails?.profile?.avatar_url ? (
                        <Image
                            src={userDetails.profile.avatar_url}
                            radius="50%"
                        />
                    ) : (
                        <IconUser />
                    )
                }
                icon={<IconUser />}
            />
            {visibleSteps.includes("hobby") && (
                <Stepper.Step
                    {...getStepProps("hobby")}
                    key="hobby"
                    label="Personal Projects"
                    description="What you do in your free time"
                    icon={<IconHammer />}
                    completedIcon={<IconHammer />}
                    disabled={!canSelectHobby}
                />
            )}
            {visibleSteps.includes("education") && (
                <Stepper.Step
                    {...getStepProps("education")}
                    key="education"
                    label="Education"
                    description="Academic background and certifications"
                    icon={<IconBellSchool />}
                    completedIcon={<IconBellSchool />}
                    disabled={!canSelectEducation}
                />
            )}
            {visibleSteps.includes("professional") && (
                <Stepper.Step
                    {...getStepProps("professional")}
                    key="professional"
                    label="Professional Experience"
                    description="What you've done in the workforce"
                    icon={<IconDeviceLaptop />}
                    completedIcon={<IconDeviceLaptop />}
                    disabled={!canSelectProfessional}
                />
            )}
            {visibleSteps.includes("proficiencies") && (
                <Stepper.Step
                    {...getStepProps("proficiencies")}
                    key="proficiencies"
                    label="Proficiencies"
                    description="How you view your skills"
                    icon={<IconStar />}
                    completedIcon={<IconStar />}
                    disabled={!canSelectProficiencies}
                />
            )}
        </Stepper>
    );
};

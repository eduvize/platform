import { Group, RingProgress, Stack, Text } from "@mantine/core";

interface RingStatisticProps {
    value: number;
    unit?: string;
    label: string;
    hideProgress?: boolean;
    textColor?: string;
    borderColor?: string;
    thickness?: number;
}

export const RingStatistic = ({
    value,
    unit,
    label,
    hideProgress,
    textColor,
    borderColor,
    thickness,
}: RingStatisticProps) => {
    return (
        <Stack gap={0} align="center">
            <RingProgress
                size={180}
                thickness={thickness || 7}
                sections={
                    hideProgress
                        ? [
                              {
                                  value: 100,
                                  color: borderColor || "#51cf66",
                              },
                          ]
                        : [
                              {
                                  value,
                                  color: borderColor || "#51cf66",
                              },
                              {
                                  value: 100 - value,
                                  color: "transparent",
                              },
                          ]
                }
                label={
                    unit ? (
                        <Stack justify="center" align="center" gap={0}>
                            <Text
                                ff="Roboto"
                                c={textColor || "#51cf66"}
                                fw={900}
                                ta="center"
                                size="60px"
                            >
                                {value}
                            </Text>

                            <Text c={textColor || "#51cf66"} fw={600} size="lg">
                                {unit}
                            </Text>
                        </Stack>
                    ) : (
                        <Text
                            ff="Roboto"
                            c={textColor || "#51cf66"}
                            fw={900}
                            ta="center"
                            size="60px"
                        >
                            {value}
                        </Text>
                    )
                }
            />

            <Text ta="center" size="sm" c="#c9c9c9" w="50%">
                {label}
            </Text>
        </Stack>
    );
};

import { useState } from "react";
import type { Meta, StoryObj } from "@storybook/react";
import { TextInput } from ".";

const meta: Meta<typeof TextInput> = {
  title: "Molecules/TextInput",
  component: TextInput,
  parameters: { layout: "centered" },
  tags: ["autodocs"],
  decorators: [(Story) => <div style={{ width: "320px" }}><Story /></div>],
};
export default meta;

type Story = StoryObj<typeof TextInput>;

export const Default: Story = {
  render: () => {
    const [v, setV] = useState("");
    return <TextInput id="title" label="Titel" value={v} onChange={setV} placeholder="Szene benennen…" />;
  },
};

export const WithHelperText: Story = {
  render: () => {
    const [v, setV] = useState("");
    return (
      <TextInput
        id="slug"
        label="Kurztitel"
        value={v}
        onChange={setV}
        helperText="Wird als URL-Segment verwendet. Nur Kleinbuchstaben."
      />
    );
  },
};

export const WithError: Story = {
  render: () => (
    <TextInput
      id="name"
      label="Name"
      value=""
      onChange={() => {}}
      errorMessage="Dieses Feld ist ein Pflichtfeld."
    />
  ),
};

export const Disabled: Story = {
  render: () => (
    <TextInput id="x" label="Gesperrt" value="Nicht editierbar" onChange={() => {}} disabled />
  ),
};

export const ReadOnly: Story = {
  render: () => (
    <TextInput id="x" label="Nur lesbar" value="Wert kann nicht geändert werden" onChange={() => {}} readOnly />
  ),
};

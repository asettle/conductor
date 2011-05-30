require 'spec_helper'

describe Image do
  it "should have a name" do
    i = Factory.build(:image, :name => nil)
    i.should_not be_valid

    i.name = ''
    i.should_not be_valid

    i.name = "valid name"
    i.should be_valid
  end

  it "should not have a name that is too long" do
    i = Factory.build(:image)
    i.name = 'x' * 1025
    i.should_not be_valid

    i.name = 'x' * 1024
    i.should be_valid
  end

  it "should have automatically generated uuid after save" do
    i = Factory.build(:image)
    i.save
    i.uuid.should_not be_nil
  end

  it "should have template_id" do
    i = Factory.build(:image, :template_id => nil)
    i.should_not be_valid

    i.template_id = 1
    i.should be_valid
  end

  it "should not create and build image if image already exists for specified target" do
    old = Factory(:image)
    lambda {Image.create_and_build!(old.template, old.provider_type)}.should raise_error(ImageExistsError)
  end

  it "should build image if there is provider and cloud account for specified target" do
    acc = Factory.build(:mock_provider_account)
    acc.stub!(:valid_credentials?).and_return(true)
    acc.save!
    tpl = Factory.build(:template)
    tpl.save!
    img = Image.create_and_build!(tpl, ProviderType.find_by_codename("mock"))
    Image.find(img).should == img
  end

  it "should import image" do
    image = OpenStruct.new(:id => 'mock', :name => 'mock', :description => 'imported mock', :architecture => 'i386')
    client = mock('DeltaCloud', :feature? => false, :image => image)
    account = Factory.build(:ec2_provider_account)
    account.stub!(:connect).and_return(client)
    account.stub!(:valid_credentials?).and_return(true)
    account.save!

    # Stub the `upload` class method. This saves us from requining
    # Image Warehouse daemon to be running for the tests.
    ImageWarehouseObject.send(:define_method, :upload) { nil }

    lambda do
      lambda do
        lambda do
          img = Image.import(account, 'mock', Factory(:user))
          img.should_not be_nil
          img.template.uploaded.should be_true
        end.should change(Image, :count).by(1)
      end.should change(Template, :count).by(1)
    end.should change(ProviderImage, :count).by(1)
  end
end

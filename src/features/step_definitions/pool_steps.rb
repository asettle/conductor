Given /^I am an authorised user$/ do
  @admin_permission = Factory :admin_permission
  @user = @admin_permission.user
end

Given /^I own a pool named "([^\"]*)"$/ do |name|
  @pool = Factory(:pool, :name => name)
  @user.owned_pools << @pool
end

Given /^the Pool has the following Hardware Profiles:$/ do |table|
  table.hashes.each do |hash|
    memory = Factory(:mock_hwp1_memory, :value => hash[:memory])
    storage = Factory(:mock_hwp1_storage, :value => hash[:storage])
    cpu = Factory(:mock_hwp1_cpu, :value => hash[:cpu])
    arch = Factory(:mock_hwp1_arch, :value => hash[:architecture])
    @pool.hardware_profiles << Factory(:mock_hwp1,
                                       :name => hash[:name],
                                       :memory => memory,
                                       :cpu => cpu,
                                       :storage => storage,
                                       :architecture => arch)
  end
end

Given /^the Pool has the following Realms named "([^\"]*)"$/ do |names|
  @cloud_account = Factory :mock_cloud_account
  @provider = @cloud_account.provider

  names.split(", ").each do |name|
    @pool.realms << Factory(:realm, :name => name, :provider => @provider)
  end
  @pool.cloud_accounts << @cloud_account

end

Given /^the Pool has the following Images:$/ do |table|
  table.hashes.each do |hash|
    hash["pool"] = @pool
    @pool.images << Factory(:pool_image, hash)
  end
end

Given /^there is not a pool named "([^\"]*)"$/ do |name|
  Pool.find_by_name(name).should be_nil
end

Then /^I should have a pool named "([^\"]*)"$/ do |name|
  Pool.find_by_name(name).should_not be_nil
  Pool.find_by_name(name).permissions.size.should == 1
end

Then /^I should see the following:$/ do |table|
  table.raw.each do |array|
    array.each do |text|
      Then 'I should see "' + text + '"'
    end
  end
end

Given /^the Pool has a quota with following capacities:$/ do |table|
  quota_hash = {}
  table.hashes.each do |hash|
    quota_hash[hash["resource"]] = hash["capacity"]
  end

  @quota = Factory(:quota, quota_hash)
  @pool.quota_id = @quota.id
  @pool.save
end
